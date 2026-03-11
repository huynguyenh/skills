#!/usr/bin/env python3
"""
Parse a TMS-style backlog spreadsheet and extract pipeline metrics.

Reads JSON from stdin (output of sheets.py read command).
Optionally compares against a previous snapshot to identify changes.

Usage:
    python3 sheets.py read SPREADSHEET_ID --sheet-name "Backlog" 2>/dev/null | \
        python3 parse_backlog.py [--previous /path/to/latest.json]
"""

import json
import sys
import argparse


def find_status_columns(row0, row1):
    """
    Dynamically find status columns by matching stage group headers (row 0)
    with 'Status' entries in row 1.
    """
    # Identify stage groups from row 0
    stage_names = {'BA', 'Design', 'BE', 'FE', 'QA', 'Pilot', 'Launch'}
    current_group = None
    group_ranges = {}

    # Iterate over max length of both rows to catch trailing columns
    max_len = max(len(row0), len(row1))
    for i in range(max_len):
        cell = row0[i].strip() if i < len(row0) and row0[i] else ''
        if cell in stage_names:
            current_group = cell
            group_ranges[current_group] = []
        if current_group:
            group_ranges[current_group].append(i)

    # Within each group, find 'Status' column
    status_cols = {}
    for group, indices in group_ranges.items():
        for i in indices:
            if i < len(row1) and row1[i].strip() == 'Status':
                status_cols[group.lower()] = i
                break

    return status_cols


def find_column(row1, name):
    """Find column index by header name in row 1."""
    for i, cell in enumerate(row1):
        if cell.strip() == name:
            return i
    return None


def parse_backlog(data, previous=None):
    rows = data.get('values', [])
    if len(rows) < 3:
        return {"error": "Not enough rows in backlog data"}

    row0 = rows[0]
    row1 = rows[1]
    data_rows = rows[2:]

    # Find key columns
    status_cols = find_status_columns(row0, row1)
    col_subsystem = find_column(row1, 'Sub-system')
    col_module = find_column(row1, 'Module')
    col_uc_name = find_column(row1, 'Use Case')
    col_full_uc_id = find_column(row1, 'Full UC_ID')
    col_uc_id = find_column(row1, 'UC_ID')
    col_priority = find_column(row1, 'Priority')
    col_planned_sprint = find_column(row1, 'Planned')
    col_actual_sprint = find_column(row1, 'Actual')

    # Find estimation columns (under 'Estimation (hour)' group in row 0)
    est_start = None
    for i, cell in enumerate(row0):
        if cell and 'Estimation' in cell:
            est_start = i
            break

    est_labels = ['BA', 'Design', 'FE', 'BE', 'QA']
    est_cols = {}
    if est_start is not None:
        for j, label in enumerate(est_labels):
            idx = est_start + j
            if idx < len(row1):
                est_cols[label.lower()] = idx

    # Parse all data rows
    by_subsystem = {}
    by_module = {}
    pipeline = {stage: {} for stage in status_cols}
    estimation = {k: 0.0 for k in est_cols}
    uc_statuses = {}
    uc_names = {}
    total_ucs = 0

    for row in data_rows:
        # Skip empty rows
        if not row or (col_subsystem is not None and
                       (col_subsystem >= len(row) or not row[col_subsystem])):
            continue

        total_ucs += 1

        # Sub-system counts
        if col_subsystem is not None and col_subsystem < len(row):
            ss = row[col_subsystem]
            by_subsystem[ss] = by_subsystem.get(ss, 0) + 1

        # Module counts
        if col_module is not None and col_module < len(row):
            mod = row[col_module]
            by_module[mod] = by_module.get(mod, 0) + 1

        # UC ID and name
        uc_id = ''
        if col_full_uc_id is not None and col_full_uc_id < len(row):
            uc_id = row[col_full_uc_id]
        elif col_uc_id is not None and col_uc_id < len(row):
            uc_id = row[col_uc_id]

        if col_uc_name is not None and col_uc_name < len(row):
            uc_names[uc_id] = row[col_uc_name]

        # Pipeline statuses
        uc_status = {}
        for stage, col_idx in status_cols.items():
            if col_idx < len(row) and row[col_idx]:
                status = row[col_idx].strip()
                pipeline[stage][status] = pipeline[stage].get(status, 0) + 1
                uc_status[stage] = status
            else:
                uc_status[stage] = ''

        if uc_id:
            uc_statuses[uc_id] = uc_status

        # Estimation hours
        for label, col_idx in est_cols.items():
            if col_idx < len(row) and row[col_idx]:
                val = row[col_idx].strip()
                if val.lower() not in ('n/a', 'na', '', '-'):
                    try:
                        estimation[label] += float(val)
                    except ValueError:
                        pass

    # Compute changes against previous snapshot
    changes = []
    if previous and 'uc_statuses' in previous:
        prev_statuses = previous['uc_statuses']
        for uc_id, current in uc_statuses.items():
            if uc_id in prev_statuses:
                prev = prev_statuses[uc_id]
                for stage in current:
                    curr_val = current.get(stage, '')
                    prev_val = prev.get(stage, '')
                    if curr_val != prev_val and (curr_val or prev_val):
                        changes.append({
                            'uc_id': uc_id,
                            'name': uc_names.get(uc_id, ''),
                            'stage': stage,
                            'from': prev_val or '(empty)',
                            'to': curr_val or '(empty)'
                        })
            else:
                # New UC not in previous snapshot
                changes.append({
                    'uc_id': uc_id,
                    'name': uc_names.get(uc_id, ''),
                    'stage': 'new',
                    'from': '',
                    'to': 'Added to backlog'
                })

    # Compute delta summaries for pipeline
    pipeline_deltas = {}
    if previous and 'pipeline' in previous:
        for stage in pipeline:
            prev_stage = previous['pipeline'].get(stage, {})
            curr_stage = pipeline[stage]
            all_statuses = set(list(prev_stage.keys()) + list(curr_stage.keys()))
            stage_delta = {}
            for status in all_statuses:
                diff = curr_stage.get(status, 0) - prev_stage.get(status, 0)
                if diff != 0:
                    stage_delta[status] = diff
            if stage_delta:
                pipeline_deltas[stage] = stage_delta

    return {
        'total_ucs': total_ucs,
        'by_subsystem': by_subsystem,
        'by_module': by_module,
        'pipeline': pipeline,
        'pipeline_deltas': pipeline_deltas,
        'estimation_hours': estimation,
        'changes': changes,
        'uc_statuses': uc_statuses,
        'uc_names': uc_names
    }


def main():
    parser = argparse.ArgumentParser(description='Parse TMS backlog spreadsheet')
    parser.add_argument('--previous', help='Path to previous snapshot JSON')
    args = parser.parse_args()

    # Read spreadsheet data from stdin
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Failed to parse input JSON: {e}"}))
        sys.exit(1)

    # Load previous snapshot if provided
    previous = None
    if args.previous:
        try:
            with open(args.previous) as f:
                previous = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # No previous snapshot — that's fine

    result = parse_backlog(data, previous)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
