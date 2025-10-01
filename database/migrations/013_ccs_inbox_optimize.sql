-- saff_orders jadvali uchun indekslar
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_saff_ccs_active_created
    ON saff_orders (created_at, id)
    WHERE status='in_call_center_supervisor' AND is_active=TRUE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_saff_status_active
    ON saff_orders (status, is_active);
