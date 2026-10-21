import sys, json, copy, io, os, numpy as np, trimesh
sys.path.insert(0, '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad/scripts')
from partsconfig import PARTS, GROUPS
from write3mf import write
from render import render
from PIL import Image
S = '/tmp/claude-0/-home-claude/1172885a-8b6c-57ab-924f-cb9398cceab1/scratchpad'
B = os.environ.get('BUILD', f'{S}/build'); OUT = os.environ.get('OUT', f'{S}/out'); os.makedirs(OUT, exist_ok=True)
PREFIX = os.environ.get('PREFIX', 'Larynx_lifesize')
V2 = os.environ.get('V2') == '1'
XM = -0.65                      # mid-sagittal plane (mean centre of hyoid/thyroid/cricoid/trachea)
PIN_D = 2.0
SCALE = float(os.environ.get('SCALE', '1.0'))
PARTM = {}
for pid, name, concepts, grp, pri, kind in PARTS:
    fp = f'{B}/final_{pid:02d}.ply'
    if os.path.exists(fp):
        m = trimesh.load(fp, process=False)
        c = m.copy(); c.merge_vertices(); c.update_faces(c.nondegenerate_faces()); c.update_faces(c.unique_faces()); c.remove_unreferenced_vertices()
        if c.is_watertight and c.is_winding_consistent and abs(c.volume - m.volume) < 1e-3 * abs(m.volume): m = c   # drop zero-area slivers
        PARTM[pid] = (name, grp, m)
_zmin = min(m.bounds[0, 2] for _, _, m in PARTM.values()); _ymid = np.mean([m.bounds[:, 1].mean() for _, _, m in PARTM.values()])
SORG = np.array([XM, _ymid, _zmin])
if SCALE != 1.0:
    for pid in PARTM:
        n, g, m = PARTM[pid]; m.vertices = SORG + (m.vertices - SORG) * SCALE
def pin_site(pid, ymin=None):
    import shapely
    from shapely.ops import unary_union
    m = PARTM[pid][2]
    sct = m.section(plane_origin=[XM, 0, 0], plane_normal=[1, 0, 0])
    T = np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, -XM], [0, 0, 0, 1]])
    pp, _ = sct.to_2D(to_2D=T); U = unary_union(list(pp.polygons_full))
    if ymin is not None: U = U.intersection(shapely.geometry.box(ymin, -1e4, 1e4, 1e4))
    g = max(getattr(U, 'geoms', [U]), key=lambda q: q.area)
    l = shapely.maximum_inscribed_circle(g); (y, z) = l.coords[0]
    return (y, z), l.length
if V2:
    import igl
    def best_site(pid, dep, ys, zs):
        m = PARTM[pid][2]
        V = np.ascontiguousarray(m.vertices); F = np.ascontiguousarray(m.faces, np.int64)
        a = np.linspace(0, 2 * np.pi, 24, endpoint=False); xs = np.linspace(-dep, dep, int(dep * 5) + 1)
        base = np.array([[x, PIN_D / 2 * np.cos(t), PIN_D / 2 * np.sin(t)] for x in xs for t in a] + [[-dep, 0, 0], [dep, 0, 0]])
        idx = [(y, z) for y in ys for z in zs]
        S = igl.signed_distance(np.vstack([base + [XM, y, z] for y, z in idx]), V, F)[0].reshape(len(idx), -1)
        md = -S.max(1); k = int(np.argmax(md)); return idx[k], md[k]
    DH, DC = 4.0 * SCALE, 2.5 * SCALE
    hb = PARTM[1][2].vertices; hb = hb[np.abs(hb[:, 0] - XM) < 3 * SCALE]
    s1, m1 = best_site(1, DH, np.arange(hb[:, 1].min(), hb[:, 1].max(), 0.25), np.arange(hb[:, 2].min(), hb[:, 2].max(), 0.25))
    cb = PARTM[3][2].vertices; cb = cb[(np.abs(cb[:, 0] - XM) < 3 * SCALE) & (cb[:, 1] > SORG[1] + (-97 - SORG[1]) * SCALE)]
    s3, m3 = best_site(3, DC, np.arange(cb[:, 1].min(), cb[:, 1].max(), 0.25), np.arange(cb[:, 2].min(), cb[:, 2].max(), 0.25))
    PINS = [(s1, DH), (s3, DC)]
    print('pin sites (y,z), depth per side, wall left around the hole:', [(np.round(s1, 2), DH, round(m1, 2)), (np.round(s3, 2), DC, round(m3, 2))])
else:
    PINS = [((-119.9, 1432.6), 4.0), ((-91.9, 1399.1), 3.2)]   # (y,z) on the cut plane, depth per side
COLOURS = {1: '#F7E6DE', 2: '#0086D6', 3: '#F4EE2A', 4: '#F55A74', 5: '#C12E2A', 6: '#FFB9A8', 7: '#F8D56B'}      # PLA Basic beige / cyan / yellow / pink / red / salmon (mucosa) / sunflower yellow (fat)
NAMES = {1: 'Bone (beige)', 2: 'Hyaline cartilage (cyan)', 3: 'Elastic cartilage (yellow)', 4: 'Ligament and membrane (pink)', 5: 'Muscle (red)', 6: 'Mucosa and fold cover (salmon)', 7: 'Fat (yellow)'}
NSLOT = int(os.environ.get('NSLOT', str(max(g for _, g, _ in PARTM.values()))))     # filament slots in the multi-colour file; groups above NSLOT share the last slot
SLOT = {g: min(g, NSLOT) for g in COLOURS}

parts = [PARTM[p[0]] for p in PARTS if p[0] in PARTM]
allV = np.vstack([m.vertices for _, _, m in parts])
ctr = np.array([(allV[:, 0].min() + allV[:, 0].max()) / 2, (allV[:, 1].min() + allV[:, 1].max()) / 2, 0])

def base_settings(multi):
    d = json.load(open(f'{S}/extract/Metadata/project_settings.config'))
    d['wall_generator'] = 'arachne'
    d['wall_loops'] = '3'
    d['layer_height'] = '0.16'
    d['brim_type'] = 'outer_only'; d['brim_width'] = '5'
    d['enable_support'] = '1'; d['support_type'] = 'tree(auto)'; d['support_threshold_angle'] = '30'
    d['support_on_build_plate_only'] = '1'
    d['different_settings_to_system'][0] = ';'.join(sorted(set(d['different_settings_to_system'][0].split(';') + [
        'wall_generator', 'wall_loops', 'layer_height', 'brim_type', 'brim_width', 'support_on_build_plate_only'])))
    if not multi: return d
    N = NSLOT
    d['wipe_tower_x'] = [os.environ.get('WT_X', '8')]; d['wipe_tower_y'] = [os.environ.get('WT_Y', '8')]      # front-left corner: the 6-slot tower is too deep for the strip beside the model at y 142
    fkeys = set('''activate_air_filtration additional_cooling_fan_speed additional_fan_full_speed_layer chamber_temperatures circle_compensation_speed close_additional_fan_first_x_layers close_fan_the_first_x_layers complete_print_exhaust_fan_speed cool_plate_temp cool_plate_temp_initial_layer cooling_perimeter_transition_distance cooling_slowdown_logic counter_coef_1 counter_coef_2 counter_coef_3 counter_limit_max counter_limit_min diameter_limit during_print_exhaust_fan_speed eng_plate_temp eng_plate_temp_initial_layer fan_cooling_layer_time fan_max_speed fan_min_speed filament_adaptive_volumetric_speed filament_adhesiveness_category filament_bridge_speed filament_change_length filament_contact_safe filament_cooling_before_tower filament_cost filament_density filament_deretraction_speed filament_dev_ams_drying_ams_limitations filament_dev_ams_drying_heat_distortion_temperature filament_dev_ams_drying_temperature filament_dev_ams_drying_time filament_dev_chamber_drying_bed_temperature filament_dev_chamber_drying_time filament_dev_drying_cooling_temperature filament_dev_drying_softening_temperature filament_diameter filament_emission_safe filament_enable_overhang_speed filament_end_gcode filament_extruder_compatibility filament_extruder_variant filament_flow_ratio filament_flush_temp filament_flush_temp_fast filament_flush_volumetric_speed filament_id filament_ingredients_safe filament_is_support filament_long_retractions_when_cut filament_long_retractions_when_ec filament_max_volumetric_speed filament_metal_stickiness filament_minimal_purge_on_wipe_tower filament_overhang_1_4_speed filament_overhang_2_4_speed filament_overhang_3_4_speed filament_overhang_4_4_speed filament_overhang_totally_speed filament_pre_cooling_temperature filament_pre_cooling_temperature_nc filament_preheat_temperature_delta filament_prime_volume filament_prime_volume_nc filament_printable filament_ramming_travel_time filament_ramming_travel_time_nc filament_ramming_volumetric_speed filament_ramming_volumetric_speed_nc filament_retract_before_wipe filament_retract_length_nc filament_retract_restart_extra filament_retract_when_changing_layer filament_retraction_distances_when_cut filament_retraction_distances_when_ec filament_retraction_length filament_retraction_minimum_travel filament_retraction_speed filament_scarf_gap filament_scarf_height filament_scarf_length filament_scarf_seam_type filament_settings_id filament_shrink filament_soluble filament_start_gcode filament_tower_interface_pre_extrusion_dist filament_tower_interface_pre_extrusion_length filament_tower_interface_print_temp filament_tower_interface_purge_volume filament_tower_ironing_area filament_type filament_velocity_adaptation_factor filament_vendor filament_wipe filament_wipe_distance filament_z_hop filament_z_hop_types full_fan_speed_layer hole_coef_1 hole_coef_2 hole_coef_3 hole_limit_max hole_limit_min hot_plate_temp hot_plate_temp_initial_layer impact_strength_z long_retractions_when_ec no_slow_down_for_cooling_on_outwalls nozzle_temperature nozzle_temperature_initial_layer nozzle_temperature_range_high nozzle_temperature_range_low overhang_fan_speed overhang_fan_threshold override_process_overhang_speed reduce_fan_stop_start_freq required_nozzle_HRC retraction_distances_when_ec slow_down_for_layer_cooling slow_down_layer_time slow_down_min_speed supertack_plate_temp supertack_plate_temp_initial_layer temperature_vitrification textured_plate_temp textured_plate_temp_initial_layer volumetric_speed_coefficients
        filament_colour_type filament_ids filament_map filament_volume_map filament_nozzle_map filament_multi_colour filament_is_mixed filament_mixed_components filament_mixed_gradient filament_mixed_gradient_curve filament_mixed_gradient_per_part filament_mixed_gradient_range filament_mixed_sublayer_ratios default_filament_colour'''.split())
    for k in fkeys:
        if k in d and isinstance(d[k], list):
            d[k] = d[k] * N
    d['filament_colour'] = [COLOURS[g] for g in range(1, N + 1)]
    d['filament_multi_colour'] = list(d['filament_colour'])
    d['filament_self_index'] = [str(i + 1) for i in range(N)]
    d['flush_volumes_matrix'] = [('0' if i == j else '300') for i in range(N) for j in range(N)]
    d['flush_volumes_vector'] = ['140'] * (2 * N)
    dst = d['different_settings_to_system']
    d['different_settings_to_system'] = [dst[0]] + [dst[1]] * N + [dst[-1]]
    return d

def thumb(objs):
    Vs, Fs, Cs, off = [], [], [], 0
    rgb = {g: tuple(int(COLOURS[g][i:i+2], 16) / 255 for i in (1, 3, 5)) for g in COLOURS}
    for o in objs:
        for p in o['parts']:
            V = p['V'] + np.array([o.get('offset', (0, 0))[0], o.get('offset', (0, 0))[1], 0])
            Vs.append(V); Fs.append(p['F'] + off); off += len(V); Cs += [rgb[p['grp']]] * len(p['F'])
    V = np.vstack(Vs); V -= (V.min(0) + V.max(0)) / 2
    im = render(V, np.vstack(Fs), 25, 20, size=512, colors=np.array(Cs))
    b = io.BytesIO(); Image.fromarray(im).save(b, 'PNG'); return b.getvalue()

meta = {'Title': os.environ.get('TITLE', 'Larynx and upper trachea, life size (BodyParts3D 4.0 rebuild)' + (', v2' if V2 else '')), 'Designer': 'Brandon',
        'License': 'CC BY 4.0 (source: BodyParts3D, (c) The Database Center for Life Science, CC Attribution 4.0 International)',
        'Description': 'Life-size laryngeal skeleton with membranes, ligaments and vocal-fold muscles, rebuilt from BodyParts3D 4.0. Membranes thickened to a 1.2 mm print minimum.' + (' ' + os.environ.get('DESC', 'Version 2: vocal folds in the quiet-breathing position; cricoid lamina lengthened and subglottis deepened toward published adult norms.') if V2 else '')}

def whole(multi):
    ps = [dict(name=n, V=m.vertices - ctr, F=m.faces, extruder=(SLOT[g] if multi else 1), grp=g) for n, g, m in parts]
    return [dict(name='Larynx (life size)', parts=ps, offset=(float(os.environ.get('OFF_X', '0')), float(os.environ.get('OFF_Y', '0'))))]   # OFF_Y>0 moves the whole model toward the back, clearing the front-left corner for the wipe tower

import manifold3d as mf
def to_mf(m):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32)))
def from_mf(M):
    me = M.to_mesh(); return trimesh.Trimesh(np.asarray(me.vert_properties)[:, :3], np.asarray(me.tri_verts), process=False)
HOLE_REPORT = []
def halves(multi):
    pin = None
    for (y, z), dep in PINS:
        c = mf.Manifold.cylinder(2 * dep, PIN_D / 2, PIN_D / 2, 48, True)        # along z, centred
        c = c.rotate([0, 90, 0]).translate([XM, y, z])
        pin = c if pin is None else pin + c
    objs = []
    HALF = os.environ.get('HALF', '')          # 'R' or 'L' to write a single half (room for the wipe tower at 2x)
    for side, label, rot in [(-1, 'Right half (patient right)', -np.pi / 2), (1, 'Left half (patient left)', np.pi / 2)]:   # cut face UP: interior stays support-free
        if HALF and ((HALF == 'R') != (side < 0)): continue
        ps = []
        for n, g, m in parts:
            M = to_mf(m)
            H = M.trim_by_plane([side, 0, 0], side * XM)   # keep the side where side*x >= side*XM
            if H.is_empty() or H.volume() < 0.3: continue
            v0 = H.volume(); H2 = H - pin; v1 = H2.volume()
            if v0 - v1 > 0.01: HOLE_REPORT.append((label, n, round(v0 - v1, 2)))
            h = from_mf(H2)
            R = trimesh.transformations.rotation_matrix(rot, [0, 1, 0], point=[XM, 0, 0])
            h.apply_transform(R)
            if HALF and os.environ.get('HALF_ROTZ') == '1': h.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 0, 1]))   # long axis along y: leaves the left strip free for the wipe tower
            assert h.is_watertight, n
            ps.append(dict(name=f'{n}', V=h.vertices, F=h.faces, extruder=(SLOT[g] if multi else 1), grp=g))
        allv = np.vstack([p['V'] for p in ps]); c = (allv.min(0) + allv.max(0)) / 2; c[2] = 0
        for p in ps: p['V'] = p['V'] - c
        half_depth = allv[:, 1].max() - allv[:, 1].min()
        objs.append(dict(name=label, parts=ps, offset=(0, 0 if HALF else (-1 if side < 0 else 1) * (half_depth / 2 + (2.5 if SCALE > 1.5 else 4.0)))))
    return objs

KINDS = ([('whole', whole), ('halves', halves)] if not os.environ.get('ONLY_WHOLE') else [('whole', whole)]) if not os.environ.get('HALF') else [('half' + os.environ['HALF'], halves)]
MULTIS = (False, True) if not (os.environ.get('ONLY_MULTI') or os.environ.get('ONLY_SINGLE')) else ((True,) if os.environ.get('ONLY_MULTI') else (False,))
for kind, fn in KINDS:
    for multi in MULTIS:
        objs = fn(multi)
        st = base_settings(multi)
        if kind.startswith('half'):
            st['brim_type'] = os.environ.get('BRIM', 'auto_brim'); st['support_on_build_plate_only'] = '0'     # BRIM=no_brim when the half spans the whole bed
            if SCALE > 1.5: st['brim_width'] = '3'
        name = f'{PREFIX}_{kind}_{f"{NSLOT}colour" if multi else "1colour"}.3mf'
        write(f'{OUT}/{name}', objs, project_settings=st, metadata=meta, thumbnail_png=thumb(objs))
        nf = sum(len(p['F']) for o in objs for p in o['parts'])
        if kind.startswith('half') and not multi: print('pin holes cut:', HOLE_REPORT)
        print(name, 'objects', len(objs), 'parts', sum(len(o['parts']) for o in objs), 'faces', nf, '%.1f MB' % (os.path.getsize(f'{OUT}/{name}') / 1e6))
