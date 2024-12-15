import rhinoscriptsyntax as rs
import random

rs.EnableRedraw(False)


def vector_field(pt, attractor, length):
    vecSum = [0,0,0]
    polyline_pts = []
    midpoints = []
    vectors = []
    max_dis = 20
    min_dis = 2
    new_vec = attractor[0]
    
    for line in attractor:
        start_pt = rs.CurveStartPoint(line)
        mid_pt = rs.CurveMidPoint(line)
        end_pt = rs.CurveEndPoint(line)
        vec = rs.VectorCreate(end_pt, start_pt)
        midpoints.append(mid_pt)
        vectors.append(vec)
    for n in range(10):
        for k in range(len(attractor)):
            dis = rs.Distance(pt, midpoints[k])
            
            if dis > 0:
                if dis < min_dis:
                    dis = min_dis

                vecSum = rs.VectorAdd(vecSum, rs.VectorScale(vectors[k], 1/(dis)))
                new_vec = rs.VectorAdd(pt, vecSum)
                polyline_pts.append(new_vec)
                grid_pt = new_vec
    line = rs.AddCurve(polyline_pts, 3)
    return line

#subsurface 
def find_UV(srf, u_num, v_num, scale, mode, lines, l, modes, scales,):
    if l > 6 or scale > 15:
        print("iteration", l, "mode", modes, "scales", scales)
        return 
    pt_dict = {}
    normal_vec = {}
    vec = {}
    zAxis = [0, 0, 1]
    line = None
    print("(u,v)", u_num, v_num)
    if len(lines) != 0:
        attractor = random.sample(lines, 3)
        lines = []
    else:
        attractor = []
        for k in range(3):
            attractor.append(rs.AddLine((10,k*10, 1), (k*10, 0, 20)))
        rs.HideObjects(attractor)
    
    attractor_pt = []
    for line in attractor:
         mid_pt = rs.CurveMidPoint(line)
         attractor_pt.append(mid_pt)
    
        
    u_domain = rs.SurfaceDomain(srf, 1) #3.0, range of width length
    v_domain = rs.SurfaceDomain(srf, 0) #3.3,
    
    u_spacing = u_domain[1]/u_num
    v_spacing = v_domain[1]/v_num
    
    color = (u_num**4 % 255, v_num**2 % 255, u_num**2 % 255)
#    color = (0, 0, 0)
    for j in range(u_num):
        for i in range(v_num):
            u = v_spacing * i
            v = u_spacing * j
            
            point = rs.EvaluateSurface(srf, u,v) #point3d

            pt_dict[(i, j)] = point #lower points
            normal = rs.SurfaceNormal(srf, [u,v]) #SurfaceClosestPoint or UV param
            
            index = rs.PointArrayClosestPoint(attractor_pt, point)
            dis = rs.Distance(attractor_pt[index], point)

            if mode == 0: #normal
                vec[(i, j)] = rs.VectorAdd(point, normal*scale*5/dis)
                if rs.Distance(vec[(i, j)], point) > 0.001:
                    line = rs.AddLine(point, vec[(i, j)])
                    
            if mode == 1: #cross
                cross = rs.VectorCrossProduct(normal, zAxis)
                axis = rs.VectorAdd(point, normal)
                pt = rs.VectorAdd(point, cross*scale*10) 
                pt = rs.VectorRotate(pt, dis%90, axis)
                if rs.Distance(pt, point) > 0.001 and rs.Distance(pt, point) < 30:
                    line = rs.AddLine(point, pt)
                    
            if mode == 2: #diagonal
                if i != 0 and j != 0:
                    diagonal = rs.VectorSubtract(point, pt_dict[(i - 1, j - 1)])
                    vec[(i, j)] = rs.VectorAdd(point, diagonal*scale*10/dis) 
                    if rs.Distance(vec[(i, j)], point) > 0.001  and rs.Distance(vec[(i, j)], point) < 30:
                        line = rs.AddLine(point, vec[(i, j)])
                    
            if mode == 3: #horizontal
                if i != 0:
                    horizon = rs.VectorSubtract(point, pt_dict[(i - 1, j)])
                    vec[(i, j)] = rs.VectorAdd(point, horizon*scale*10/dis) 
                    if rs.Distance(vec[(i, j)], point) > 0.001 and rs.Distance(vec[(i, j)], point) < 30:
                        line = rs.AddLine(point, vec[(i, j)])
                    
            if mode == 4: #vertical
                if j != 0:
                    vertical = rs.VectorSubtract(point, pt_dict[(i, j - 1)])
                    vec[(i, j)] = rs.VectorAdd(point, vertical*scale*10/dis)
                    if rs.Distance(vec[(i, j)], point) > 0.001  and rs.Distance(vec[(i, j)], point) < 30:
                        line = rs.AddLine(point, vec[(i, j)])
                    
            if mode > 4:
                line = vector_field(point, attractor, dis)
                
                    
            if line:
                lines.append(line)
                rs.ObjectColor(line, color)
                
    u_num = u_num **3 % 223
    v_num = u_num **3 % 317
    modes[l] = 4 #recordds dw  old modes
    scales[l] = scale
    mode = random.choice([i for i in range(0, 6) if i != mode])
    scale = random.uniform(0.7, 3)

    return find_UV(srf, u_num, v_num, scale, mode, lines, l + 1, modes, scales)

#srf = rs.AddSphere((0,0,0), 100)
srf = rs.GetObject("click the surface")
u = 146
v = 157
scale = 1.2
mode = random.randint(0, 5)
find_UV(srf, u, v, scale, mode, [], 0, {}, {})

