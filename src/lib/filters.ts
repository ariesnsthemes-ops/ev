/** Option and group shapes for the FilterSidebar component. */
export interface FilterOption { name: string; value: string; label: string; count?: number | null; checked?: boolean }
export interface FilterGroup { id: string; legend: string; items: FilterOption[]; more?: boolean; skipZero?: boolean }
