# Metadata Migration Repair — v0.2

- Repaired timestamp fields (created_at/updated_at set to null for migrated): 384 connections
- Repaired evidence stance (removed fabricated supports for migrated): 42 evidence items
- Repaired entities updated_at: 128
- Preserved genuine: 0 connections (manual curated retain review_history, evidence description, source dates)
- Records affected: 384 connections + 128 entities
- Records unchanged: 0

Preserved: review_history, human review timestamps, actual source dates, evidence descriptions, canonicalization metadata where real.
