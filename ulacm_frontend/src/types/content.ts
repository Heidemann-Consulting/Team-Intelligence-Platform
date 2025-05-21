// File: ulacm_frontend/src/types/content.ts
// Purpose: TypeScript types specific to Content Items and Versions.
// No changes needed based on the current request, but providing the full file for completeness.
export interface VersionMeta {
    version_id: string;
    version_number: number;
    saved_by_team_id: string;
    created_at: string; // Version save timestamp (ISO string)
}

// Detailed version content (SRS 8.5.1)
export interface ContentVersionDetails extends VersionMeta {
    item_id: string;
    markdown_content: string;
}

// Response when listing versions (SRS 8.5.2)
export interface ContentVersionListResponse {
    total_count: number; // Renamed from total_versions for consistency
    item_id: string;
    offset: number;
    limit: number;
    versions: VersionMeta[];
}

// Response when saving a new version (SRS 8.5.3)
export interface SaveVersionResponse {
    item_id: string;
    new_version: ContentVersionDetails; // Details of the newly created version
    item_updated_at: string; // Timestamp of when the parent ContentItem was updated (ISO string)
}
