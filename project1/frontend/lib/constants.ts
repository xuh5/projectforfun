type NodeTypeOption = {
  value: string;
  label: string;
};

type SectorOption = {
  value: string;
  label: string;
  sampleLabel?: string;
};

export const NODE_TYPE_OPTIONS: readonly NodeTypeOption[] = [
  { value: 'company', label: 'Company' },
  { value: 'person', label: 'Person' },
  { value: 'project', label: 'Project' },
  { value: 'organization', label: 'Organization' },
] as const;

export const SECTOR_OPTIONS: readonly SectorOption[] = [
  { value: 'ai', label: 'Artificial Intelligence', sampleLabel: 'AI' },
  { value: 'automotive', label: 'Automotive' },
  { value: 'consumer', label: 'Consumer' },
  { value: 'enterprise', label: 'Enterprise' },
  { value: 'cloud', label: 'Cloud' },
  { value: 'semiconductors', label: 'Semiconductors' },
  { value: 'finance', label: 'Finance' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'energy', label: 'Energy' },
  { value: 'industrial', label: 'Industrial' },
] as const;

export const SECTOR_SAMPLE_LABELS = SECTOR_OPTIONS.map((option) => option.sampleLabel ?? option.label);

type RelationTypeOption = {
  value: string;
  label: string;
};

export const RELATION_TYPE_OPTIONS: readonly RelationTypeOption[] = [
  { value: 'owns', label: 'Owns' },
  { value: 'partners_with', label: 'Partners With' },
  { value: 'competes_with', label: 'Competes With' },
  { value: 'supplies_to', label: 'Supplies To' },
  { value: 'works_with', label: 'Works With' },
  { value: 'invests_in', label: 'Invests In' },
  { value: 'subsidiary_of', label: 'Subsidiary Of' },
  { value: 'collaborates_with', label: 'Collaborates With' },
] as const;

