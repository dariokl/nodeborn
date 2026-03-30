from __future__ import annotations

from math import floor
import random

from nodeborn.colony.map import ColonyMap, TerrainType, Tile

DEFAULT_MAP_WIDTH = 128
DEFAULT_MAP_HEIGHT = 128
START_CLEAR_RADIUS = 5

ELEVATION_ROCK_THRESHOLD = 0.92
ELEVATION_MOUNTAIN_THRESHOLD = 0.78
ELEVATION_WATER_THRESHOLD = 0.14

MOISTURE_RIVER_THRESHOLD = 0.70
MOISTURE_SAND_THRESHOLD = 0.18
MOISTURE_FOREST_THRESHOLD = 0.74
MOISTURE_PLAINS_THRESHOLD = 0.52

BASE_FERTILITY = 0.35
MOISTURE_FERTILITY_MULTIPLIER = 0.65
PLAINS_FERTILITY_BONUS = 0.10
FOREST_FERTILITY_BONUS = 0.05
SAND_FERTILITY_PENALTY = 0.25

WATER_BODY_RADIUS_X_MIN = 2
WATER_BODY_RADIUS_X_MAX = 5
WATER_BODY_RADIUS_Y_MIN = 2
WATER_BODY_RADIUS_Y_MAX = 4
WATER_BODY_EDGE_NOISE_MAX = 0.20

MOUNTAIN_CLUSTER_RADIUS_MIN = 2
MOUNTAIN_CLUSTER_RADIUS_MAX = 4
MOUNTAIN_CORE_ROCK_CHANCE = 0.35

FOREST_SCATTER_CHANCE = 0.16
FOREST_RADIUS_ONE_CHANCE = 0.85
FOREST_SPREAD_CHANCE = 0.75


def generate_map(
    width: int = DEFAULT_MAP_WIDTH,
    height: int = DEFAULT_MAP_HEIGHT,
    seed: int = random.randint(0, 999999),
) -> ColonyMap:
    """Generate a deterministic colony map from width/height/seed."""
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")

    rng = random.Random(seed)
    center = (width // 2, height // 2)

    elevation_map = [
        [_fractal_value_noise(x, y, seed + 11) for x in range(width)]
        for y in range(height)
    ]
    moisture_map = [
        [_fractal_value_noise(x, y, seed + 97) for x in range(width)]
        for y in range(height)
    ]

    terrain_grid: list[list[TerrainType]] = []
    for y in range(height):
        terrain_row: list[TerrainType] = []
        for x in range(width):
            terrain_row.append(_assign_terrain(
                elevation_map[y][x], moisture_map[y][x]))
        terrain_grid.append(terrain_row)

    _paint_water_bodies(terrain_grid, width, height, rng, center)
    _paint_mountain_clusters(terrain_grid, width, height, rng, center)
    _scatter_forests(terrain_grid, width, height, rng, center)
    _clear_starting_area(terrain_grid, width, height, center, seed)

    _ensure_presence(terrain_grid, TerrainType.WATER, rng, center)
    _ensure_presence(terrain_grid, TerrainType.MOUNTAIN, rng, center)
    _ensure_presence(terrain_grid, TerrainType.FOREST, rng, center)

    tiles: list[list[Tile]] = []
    for y in range(height):
        tile_row: list[Tile] = []
        for x in range(width):
            terrain = terrain_grid[y][x]
            moisture = moisture_map[y][x]
            tile_row.append(
                Tile(
                    x=x,
                    y=y,
                    terrain=terrain,
                    fertility=_fertility_for(terrain, moisture),
                    elevation=elevation_map[y][x],
                )
            )
        tiles.append(tile_row)

    return ColonyMap(width=width, height=height, tiles=tiles, seed=seed)


def _assign_terrain(elevation: float, moisture: float) -> TerrainType:
    if elevation >= ELEVATION_ROCK_THRESHOLD:
        return TerrainType.ROCK
    if elevation >= ELEVATION_MOUNTAIN_THRESHOLD:
        return TerrainType.MOUNTAIN
    if elevation <= ELEVATION_WATER_THRESHOLD:
        return TerrainType.RIVER if moisture >= MOISTURE_RIVER_THRESHOLD else TerrainType.WATER
    if moisture <= MOISTURE_SAND_THRESHOLD:
        return TerrainType.SAND
    if moisture >= MOISTURE_FOREST_THRESHOLD:
        return TerrainType.FOREST
    if moisture >= MOISTURE_PLAINS_THRESHOLD:
        return TerrainType.PLAINS
    return TerrainType.GRASS


def _fertility_for(terrain: TerrainType, moisture: float) -> float:
    if terrain in {
        TerrainType.WATER,
        TerrainType.RIVER,
        TerrainType.MOUNTAIN,
        TerrainType.ROCK,
    }:
        return 0.0

    fertility = BASE_FERTILITY + (MOISTURE_FERTILITY_MULTIPLIER * moisture)
    if terrain is TerrainType.PLAINS:
        fertility += PLAINS_FERTILITY_BONUS
    elif terrain is TerrainType.FOREST:
        fertility += FOREST_FERTILITY_BONUS
    elif terrain is TerrainType.SAND:
        fertility -= SAND_FERTILITY_PENALTY

    return _clamp01(fertility)


def _paint_water_bodies(
    grid: list[list[TerrainType]],
    width: int,
    height: int,
    rng: random.Random,
    center: tuple[int, int],
) -> None:
    count = max(2, (width * height) // 900)
    for _ in range(count):
        cx = rng.randrange(width)
        cy = rng.randrange(height)
        if _distance_sq((cx, cy), center) <= (START_CLEAR_RADIUS + 2) ** 2:
            continue

        radius_x = rng.randint(WATER_BODY_RADIUS_X_MIN,
                               WATER_BODY_RADIUS_X_MAX)
        radius_y = rng.randint(WATER_BODY_RADIUS_Y_MIN,
                               WATER_BODY_RADIUS_Y_MAX)
        for y in range(max(0, cy - radius_y), min(height, cy + radius_y + 1)):
            for x in range(max(0, cx - radius_x), min(width, cx + radius_x + 1)):
                norm = ((x - cx) / radius_x) ** 2 + ((y - cy) / radius_y) ** 2
                if norm <= 1.0 + (rng.random() * WATER_BODY_EDGE_NOISE_MAX):
                    if grid[y][x] in {TerrainType.ROCK, TerrainType.MOUNTAIN}:
                        continue
                    grid[y][x] = TerrainType.WATER


def _paint_mountain_clusters(
    grid: list[list[TerrainType]],
    width: int,
    height: int,
    rng: random.Random,
    center: tuple[int, int],
) -> None:
    count = max(2, (width * height) // 1200)
    for _ in range(count):
        cx = rng.randrange(width)
        cy = rng.randrange(height)
        if _distance_sq((cx, cy), center) <= (START_CLEAR_RADIUS + 2) ** 2:
            continue

        radius = rng.randint(MOUNTAIN_CLUSTER_RADIUS_MIN,
                             MOUNTAIN_CLUSTER_RADIUS_MAX)
        for y in range(max(0, cy - radius), min(height, cy + radius + 1)):
            for x in range(max(0, cx - radius), min(width, cx + radius + 1)):
                if max(abs(x - cx), abs(y - cy)) > radius:
                    continue
                if grid[y][x] in {TerrainType.WATER, TerrainType.RIVER}:
                    continue
                if max(abs(x - cx), abs(y - cy)) <= 1 and rng.random() < MOUNTAIN_CORE_ROCK_CHANCE:
                    grid[y][x] = TerrainType.ROCK
                else:
                    grid[y][x] = TerrainType.MOUNTAIN


def _scatter_forests(
    grid: list[list[TerrainType]],
    width: int,
    height: int,
    rng: random.Random,
    center: tuple[int, int],
) -> None:
    attempts = max(20, (width * height) // 3)
    for _ in range(attempts):
        if rng.random() > FOREST_SCATTER_CHANCE:
            continue

        cx = rng.randrange(width)
        cy = rng.randrange(height)
        if _distance_sq((cx, cy), center) <= (START_CLEAR_RADIUS + 1) ** 2:
            continue
        if grid[cy][cx] not in {TerrainType.GRASS, TerrainType.PLAINS}:
            continue

        radius = 1 if rng.random() < FOREST_RADIUS_ONE_CHANCE else 2
        for y in range(max(0, cy - radius), min(height, cy + radius + 1)):
            for x in range(max(0, cx - radius), min(width, cx + radius + 1)):
                if grid[y][x] in {TerrainType.GRASS, TerrainType.PLAINS} and rng.random() < FOREST_SPREAD_CHANCE:
                    grid[y][x] = TerrainType.FOREST


def _clear_starting_area(
    grid: list[list[TerrainType]],
    width: int,
    height: int,
    center: tuple[int, int],
    seed: int,
) -> None:
    cx, cy = center
    for y in range(max(0, cy - START_CLEAR_RADIUS), min(height, cy + START_CLEAR_RADIUS + 1)):
        for x in range(max(0, cx - START_CLEAR_RADIUS), min(width, cx + START_CLEAR_RADIUS + 1)):
            if _distance_sq((x, y), center) <= START_CLEAR_RADIUS**2:
                grid[y][x] = TerrainType.PLAINS if (
                    x + y + seed) % 4 == 0 else TerrainType.GRASS


def _ensure_presence(
    grid: list[list[TerrainType]],
    terrain: TerrainType,
    rng: random.Random,
    center: tuple[int, int],
) -> None:
    if any(tile is terrain for row in grid for tile in row):
        return

    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    candidates: list[tuple[int, int]] = []
    for y in range(height):
        for x in range(width):
            if _distance_sq((x, y), center) <= (START_CLEAR_RADIUS + 1) ** 2:
                continue
            if grid[y][x] in {TerrainType.GRASS, TerrainType.PLAINS, TerrainType.SAND}:
                candidates.append((x, y))

    if not candidates:
        return

    x, y = rng.choice(candidates)
    grid[y][x] = terrain


def _fractal_value_noise(x: int, y: int, seed: int) -> float:
    value = (
        (0.55 * _value_noise(x, y, seed, 16.0))
        + (0.30 * _value_noise(x, y, seed + 101, 8.0))
        + (0.15 * _value_noise(x, y, seed + 202, 4.0))
    )
    return _clamp01(value)


def _value_noise(x: int, y: int, seed: int, scale: float) -> float:
    gx = x / scale
    gy = y / scale

    x0 = floor(gx)
    y0 = floor(gy)
    x1 = x0 + 1
    y1 = y0 + 1

    sx = _smoothstep(gx - x0)
    sy = _smoothstep(gy - y0)

    n00 = _hash_to_unit(x0, y0, seed)
    n10 = _hash_to_unit(x1, y0, seed)
    n01 = _hash_to_unit(x0, y1, seed)
    n11 = _hash_to_unit(x1, y1, seed)

    ix0 = _lerp(n00, n10, sx)
    ix1 = _lerp(n01, n11, sx)
    return _lerp(ix0, ix1, sy)


def _hash_to_unit(ix: int, iy: int, seed: int) -> float:
    value = (ix * 374761393) + (iy * 668265263) + (seed * 362437)
    value = (value ^ (value >> 13)) * 1274126177
    value = value ^ (value >> 16)
    return (value & 0xFFFFFFFF) / 0xFFFFFFFF


def _distance_sq(a: tuple[int, int], b: tuple[int, int]) -> int:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return (dx * dx) + (dy * dy)


def _lerp(a: float, b: float, t: float) -> float:
    return a + ((b - a) * t)


def _smoothstep(t: float) -> float:
    return t * t * (3.0 - (2.0 * t))


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value
