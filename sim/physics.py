import math

class RobotKinematics:
    def __init__(self, length, width):
        self.length = length
        self.width = width

    def get_corners(self, x, y, theta):
        """Returns the 4 corners of the robot's footprint given its pose."""
        # Half dimensions
        hl = self.length / 2.0
        hw = self.width / 2.0

        # Corners relative to center
        corners_local = [
            (hl, hw),
            (-hl, hw),
            (-hl, -hw),
            (hl, -hw)
        ]

        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        corners_global = []
        for cx, cy in corners_local:
            rx = x + (cx * cos_t - cy * sin_t)
            ry = y + (cx * sin_t + cy * cos_t)
            corners_global.append((rx, ry))
        
        return corners_global

def polygons_overlap(poly1, poly2):
    """Checks if two convex polygons overlap using the Separating Axis Theorem (SAT)."""
    
    def get_edges(poly):
        edges = []
        for i in range(len(poly)):
            p1 = poly[i]
            p2 = poly[(i + 1) % len(poly)]
            edges.append((p2[0] - p1[0], p2[1] - p1[1]))
        return edges

    def get_axes(edges):
        axes = []
        for edge in edges:
            # Perpendicular vector (normal)
            normal = (-edge[1], edge[0])
            # Normalize
            length = math.hypot(normal[0], normal[1])
            axes.append((normal[0] / length, normal[1] / length))
        return axes

    def project(poly, axis):
        min_proj = float('inf')
        max_proj = float('-inf')
        for point in poly:
            proj = point[0] * axis[0] + point[1] * axis[1]
            min_proj = min(min_proj, proj)
            max_proj = max(max_proj, proj)
        return min_proj, max_proj

    edges1 = get_edges(poly1)
    edges2 = get_edges(poly2)
    
    axes = get_axes(edges1) + get_axes(edges2)
    
    for axis in axes:
        min1, max1 = project(poly1, axis)
        min2, max2 = project(poly2, axis)
        
        # Check for gap
        if max1 < min2 or max2 < min1:
            return False # Gap found, no overlap
            
    return True

def check_footprint_collision(pose1, size1, pose2, size2):
    """
    pose = (x, y, theta)
    size = (length, width)
    """
    k1 = RobotKinematics(size1[0], size1[1])
    k2 = RobotKinematics(size2[0], size2[1])
    
    corners1 = k1.get_corners(*pose1)
    corners2 = k2.get_corners(*pose2)
    
    return polygons_overlap(corners1, corners2)

if __name__ == "__main__":
    # Unit tests for Definition of Done
    
    # Test 1: Identical poses (overlap)
    pose1 = (0, 0, 0)
    size1 = (1.0, 0.5)
    assert check_footprint_collision(pose1, size1, pose1, size1) == True
    print("Test 1 (Identical poses) -> Overlap: True")

    # Test 2: Distinct non-overlapping
    pose2 = (2, 0, 0)
    assert check_footprint_collision(pose1, size1, pose2, size1) == False
    print("Test 2 (Distinct non-overlapping) -> Overlap: False")

    # Test 3: Touching/overlapping slightly
    pose3 = (0.9, 0, 0)
    assert check_footprint_collision(pose1, size1, pose3, size1) == True
    print("Test 3 (Overlapping slightly) -> Overlap: True")

    # Test 4: Rotated but not overlapping
    pose4 = (1.5, 0, math.pi/2)
    assert check_footprint_collision(pose1, size1, pose4, size1) == False
    print("Test 4 (Rotated non-overlapping) -> Overlap: False")

    # Test 5: Rotated and overlapping
    pose5 = (0.5, 0.5, math.pi/4)
    size5 = (1.0, 0.5)
    assert check_footprint_collision(pose1, size1, pose5, size5) == True
    print("Test 5 (Rotated overlapping) -> Overlap: True")

    print("SUCCESS: All footprint collision tests passed.")
