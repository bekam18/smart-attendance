#!/usr/bin/env python3
"""
Insert students listed in `backend/models/Classifier/labels.csv` into MongoDB.

This script will:
- Read `labels.csv` for student IDs
- For each student_id, if not already present in `students` collection, create a user and student profile
- Mark `face_registered` True if `backend/dataset/processed/{student_id}` contains images

Usage:
  python backend/scripts/insert_students_from_labels.py

"""
import os
import csv
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime
from config import config
from utils.security import hash_password


def read_labels(labels_path: Path):
    ids = []
    if not labels_path.exists():
        print(f"❌ labels.csv not found at: {labels_path}")
        return ids
    with open(labels_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Expect row like: id,name where name is student id like STU001
            name = row.get('name') or row.get('student_id') or row.get('label')
            if name:
                ids.append(name.strip())
    return ids


def main():
    model_labels = Path(config.MODEL_PATH) / 'labels.csv'
    print(f"🔍 Reading labels from: {model_labels}")
    student_ids = read_labels(model_labels)
    if not student_ids:
        print("❌ No student IDs found. Exiting.")
        return

    client = MongoClient(config.MONGODB_URI)
    db = client[config.MONGODB_DB_NAME]

    added = 0
    skipped = 0

    for sid in student_ids:
        sid = sid.strip()
        if sid == '':
            continue

        existing = db.students.find_one({'student_id': sid})
        if existing:
            print(f"⏭️ Skipping existing student: {sid}")
            skipped += 1
            continue

        # Create a minimal user account and student profile
        username = sid.lower()
        password = hash_password('stud123')
        email = f"{username}@smartattendance.com"
        name = sid  # No full name available; using student id as placeholder

        user_doc = {
            'username': username,
            'password': password,
            'email': email,
            'name': name,
            'role': 'student',
            'created_at': datetime.utcnow(),
            'enabled': True,
        }

        ures = db.users.insert_one(user_doc)
        user_id = str(ures.inserted_id)

        # Check dataset processed images for this student to set face_registered
        alt_processed = Path(__file__).resolve().parents[2] / 'dataset' / 'processed' / sid
        has_face = False
        if alt_processed.exists() and any(alt_processed.glob('*.*')):
            has_face = True

        student_doc = {
            'user_id': user_id,
            'student_id': sid,
            'name': name,
            'email': email,
            'department': 'Unknown',
            'year': 'Unknown',
            'face_registered': bool(has_face),
            'created_at': datetime.utcnow()
        }

        db.students.insert_one(student_doc)
        print(f"✅ Inserted student: {sid} (user: {username}) face_registered={student_doc['face_registered']}")
        added += 1

    print('\nSummary:')
    print(f'  Total labels processed: {len(student_ids)}')
    print(f'  Added: {added}')
    print(f'  Skipped (already existed): {skipped}')

    client.close()


if __name__ == '__main__':
    main()
