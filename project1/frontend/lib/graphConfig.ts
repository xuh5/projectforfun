/**
 * Centralized configuration for graph visualization.
 * Modify values here to adjust the appearance and behavior of the 3D graph.
 */

// ============================================================================
// Node Configuration
// ============================================================================

export const NODE_CONFIG = {
  /** Base radius of node spheres */
  radius: 0.8,

  /** Sphere geometry detail (widthSegments, heightSegments) */
  geometrySegments: [32, 32] as const,

  /** Default node color (used when node.color is not provided) */
  defaultColor: '#667eea',
} as const;

// ============================================================================
// Node Material Properties
// ============================================================================

export const NODE_MATERIAL = {
  /** Base emissive intensity (brightness) when not hovered */
  emissiveIntensity: {
    default: 0.25,
    hovered: 0.4,
  },

  /** Surface roughness (0 = mirror-like, 1 = completely rough) */
  roughness: 0.35,

  /** Metalness (0 = dielectric, 1 = metallic) */
  metalness: 0.25,
} as const;

// ============================================================================
// Node Hover Animation
// ============================================================================

export const NODE_HOVER = {
  /** Scale multiplier when hovered (1.0 = normal size, 1.5 = 150% size) */
  scaleMultiplier: 1.5,

  /** Animation interpolation speed (0.1 = smooth, higher = faster) */
  animationSpeed: 0.1,
} as const;

// ============================================================================
// Node Label/Text Configuration
// ============================================================================

export const NODE_LABEL = {
  /** Position offset above the node [x, y, z] */
  positionOffset: [0, 0.75, 0] as const,

  /** Font size */
  fontSize: 0.3,

  /** Text color */
  color: '#f8fafc',

  /** Outline width for text readability */
  outlineWidth: 0.015,

  /** Outline color */
  outlineColor: 'rgba(0, 0, 0, 0.75)',

  /** Maximum width before text wraps */
  maxWidth: 2.5,

  /** Line height multiplier */
  lineHeight: 1.1,

  /** Text alignment */
  textAlign: 'center' as const,

  /** Depth offset to prevent z-fighting */
  depthOffset: -1,
} as const;

// ============================================================================
// Edge Configuration
// ============================================================================

export const EDGE_CONFIG = {
  /** Line color */
  color: '#9ca3af',

  /** Line width in pixels */
  lineWidth: 1.5,

  /** Opacity (0 = transparent, 1 = opaque) */
  opacity: 0.35,

  /** Whether edges write to depth buffer */
  depthWrite: false,
} as const;

// ============================================================================
// Force-Directed Layout Configuration
// ============================================================================

export const FORCE_LAYOUT = {
  /** Default number of simulation iterations */
  defaultIterations: 300,

  /** Target distance between connected nodes */
  linkDistance: 1.8,

  /** Default link strength (0 = weak, 1 = strong) */
  defaultLinkStrength: 0.15,

  /** Collision detection radius */
  collisionRadius: 0.85,

  /** Collision force strength */
  collisionStrength: 0.95,

  /** Scale multiplier for initial layout size (based on cube root of node count) */
  scaleMultiplier: 6,

  /** Charge strength base (negative = repulsion) */
  chargeStrengthBase: -12,

  /** Axis force strength (keeps nodes centered) */
  axisForceStrength: 0.02,
} as const;

// ============================================================================
// Camera Configuration
// ============================================================================

export const CAMERA_CONFIG = {
  /** Initial camera position [x, y, z] */
  initialPosition: [0, 0, 8] as const,

  /** Field of view in degrees */
  fov: 45,

  /** Distance multiplier when fitting to layout */
  fitDistanceMultiplier: 2.5,

  /** Minimum camera distance */
  minDistance: 6,

  /** Near clipping plane (relative to distance) */
  nearPlaneRatio: 100,

  /** Far clipping plane (relative to distance) */
  farPlaneRatio: 10,

  /** Minimum near plane value */
  minNearPlane: 0.1,

  /** Minimum far plane value */
  minFarPlane: 50,
} as const;

// ============================================================================
// Focus Node Camera Configuration
// ============================================================================

export const FOCUS_CAMERA = {
  /** Distance multiplier when focusing on a node */
  distanceMultiplier: 0.3,

  /** Minimum focus distance */
  minDistance: 3,

  /** Near plane ratio for focus */
  nearPlaneRatio: 50,
} as const;

// ============================================================================
// Lighting Configuration
// ============================================================================

export const LIGHTING_CONFIG = {
  /** Background color */
  backgroundColor: '#05060d',

  /** Ambient light intensity */
  ambientIntensity: 0.6,

  /** Primary directional light position [x, y, z] */
  primaryDirectionalLight: {
    position: [5, 8, 5] as const,
    intensity: 0.8,
  },

  /** Secondary directional light position [x, y, z] */
  secondaryDirectionalLight: {
    position: [-6, -4, -5] as const,
    intensity: 0.35,
  },

  /** Point light position [x, y, z] */
  pointLight: {
    position: [0, 0, 0] as const,
    intensity: 0.2,
  },
} as const;

// ============================================================================
// Orbit Controls Configuration
// ============================================================================

export const ORBIT_CONTROLS = {
  /** Enable smooth damping */
  enableDamping: true,

  /** Damping factor (lower = smoother) */
  dampingFactor: 0.08,

  /** Rotation speed multiplier */
  rotateSpeed: 0.6,
} as const;

// ============================================================================
// Position Normalization
// ============================================================================

export const POSITION_CONFIG = {
  /** Scale factor for normalizing cartesian positions */
  positionScale: 120,
} as const;

