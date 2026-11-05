// 丸型ルーバーグリル(パラメトリック版)
// 単位: mm / 値はすべて写真からの推定値です。実物をノギスで測って調整してください。
//
// 座標: +Z が前面(化粧面)側。z=height が前面、z=0 が背面。
//       タブ付きの桟が X 軸、タブなしの桟が Y 軸に沿います。
// ウィンドウ > カスタマイザー から値を変更できます。
// 調整の起点は outer_d / height / flange_t / spigot_rim_out / pad_r です。

/* [外形] */
// フランジ外径
outer_d = 110;
// 全高(前面から背面まで)
height = 10;
// フランジ外周の厚み
flange_t = 4;
// フランジ前面の内周半径
flange_in_r = 49.5;
// フランジ前面側の角丸半径
flange_round = 1.0;

/* [差し込み部] */
// 背面リムの内周半径
spigot_rim_in = 46.6;
// 背面リムの外周半径(差し込み径の基準)
spigot_rim_out = 48.6;
// 厚い帯の外周半径(はめ合いを決める寸法)
pad_r = 49.7;
// 厚い帯の高さ
pad_h = 2.2;
// 厚い帯の開始角度(度)
pad_start = 10;
// 厚い帯1本あたりの角度範囲(度)
pad_span = 42;
// 厚い帯の本数
pad_count = 3; // [0:1:6]

/* [ルーバーリング: 前面内周, 前面外周, 背面内周, 背面外周] */
// 内側から1本目(半径)
ring1 = [13.4, 16.7, 9.0, 11.0];
// 2本目(半径)
ring2 = [22.5, 26.0, 18.0, 20.0];
// 3本目(半径)
ring3 = [31.7, 35.6, 27.8, 29.8];
// 4本目(半径)
ring4 = [40.8, 44.4, 37.2, 39.2];
// リング前面の面取り
ring_edge = 0.3;
// リング外壁のふくらみ(1で直線、大きいほど前面側で広がる)
ring_flare = 1.6;

/* [中央ハブ] */
// 前面の円盤半径
hub_front_r = 7.5;
// 背面の筒の外半径
hub_back_r = 5.1;
// 背面の筒の内半径
hub_bore_r = 3.2;
// 中央ピンの半径
hub_peg_r = 1.6;

/* [十字の桟] */
// 前面側の幅
spoke_w_front = 1.5;
// 背面側の幅
spoke_w_back = 2.0;
// 桟の内側の始点半径(hub_back_r より小さくすると背面でハブとつながります)
spoke_r_in = 6.0;

/* [タブ] */
// タブを付ける
show_tabs = true;
// 幅
tab_w = 8;
// 厚み
tab_t = 2.5;
// 先端の半径
tab_r_end = 54.5;

/* [指掛けのくぼみ] */
// くぼみを付ける
show_scoops = true;
// 位置(度)。反対側にもう1か所付きます
scoop_angle = 135;
// 中心の半径
scoop_r = 49.0;
// 斜面方向の半径
scoop_len = 6.3;
// 円周方向の半径
scoop_wid = 11.5;
// 斜面に垂直な方向の半径
scoop_dep = 2.2;
// 斜面の傾き(度)
scoop_tilt = 54.6;
// 裏側のふくらみの肉厚
scoop_shell = 1.3;
// 最外リングの切り欠き: 中心の半径
notch_r = 48.0;
// 切り欠き: 半径方向の大きさ
notch_sr = 5.8;
// 切り欠き: 円周方向の大きさ
notch_st = 7.8;

/* [リブ] */
// リブの本数
rib_count = 3; // [0:1:6]
// 開始角度(度)
rib_start = 81;
// 半径方向の長さ
rib_len = 3.2;
// 厚み
rib_t = 1.1;

/* [細部と出力] */
// 桟とリムの交点の小さな丸パッドを付ける
show_pin_pads = true;
// 丸パッドの半径
pin_pad_r = 1.7;
// 丸パッドの厚み
pin_pad_t = 1.0;
// 前面を下にした印刷向きで出力する(同梱のSTLと同じ向き)
print_orientation = true;
// 円周の分割数(レンダリング時)
segments = 256; // [64:8:512]
// 円周の分割数(プレビュー時)
preview_segments = 72; // [32:8:256]

/* [Hidden] */
R = outer_d / 2;
H = height;
Z_FB = H - flange_t;      // フランジ背面の高さ
RINGS = [ring1, ring2, ring3, ring4];
SEG = $preview ? preview_segments : segments;
SEG_SMALL = $preview ? 32 : max(32, floor(segments / 2));
FLARE_N = 8;

// ---- 断面形状 ----
function flare(r0, r1) = [
    for (i = [0 : FLARE_N])
        [r0 + (r1 - r0) * pow(i / FLARE_N, ring_flare), (H - ring_edge) * i / FLARE_N]
];
function rev(v) = [for (i = [len(v) - 1 : -1 : 0]) v[i]];

function body_profile() = let (c = spigot_rim_in, d = spigot_rim_out, fi = flange_in_r, fr = flange_round) concat(
    [[c, 0], [c + 0.4, 0.3 * H], [c + 1.47, 0.603 * H], [fi - 0.3, H - 0.3]],
    [[fi + 0.2, H], [R - fr, H]],
    [for (t = [20 : 14 : 90]) [R - fr + fr * sin(t), H - fr + fr * cos(t)]],
    [[R, Z_FB + 0.5], [R - 0.4, Z_FB]],
    [[d + 2.8, Z_FB], [d + 1.7, Z_FB - 0.5], [d + 1.0, Z_FB - 1.3],
     [d + 0.6, 0.5 * Z_FB], [d + 0.3, 0.25 * Z_FB], [d, 0]]
);

function hub_profile() = let (f = hub_front_r, b = hub_back_r, k = f - b) [
    [hub_bore_r, 0], [b, 0],
    [b + k / 12, 0.25 * H], [b + k / 3, 0.5 * H], [b + k * 17 / 24, 0.75 * H],
    [f, H - 0.3], [f - 0.3, H],
    [1.2, H], [0.9, H - 0.25], [0, H - 0.35],
    [0, 0.45 * H], [hub_peg_r - 0.4, 0.45 * H], [hub_peg_r - 0.1, 0.5 * H],
    [hub_peg_r, 0.75 * H], [hub_bore_r - 0.2, 0.75 * H]
];

function bore_profile() = [
    [0, -1], [hub_bore_r, -1], [hub_bore_r, 0],
    [hub_bore_r - 0.2, 0.75 * H], [hub_peg_r, 0.75 * H],
    [hub_peg_r - 0.1, 0.5 * H], [hub_peg_r - 0.4, 0.45 * H], [0, 0.45 * H]
];

// ---- 部品 ----
module revolve(pts) { rotate_extrude($fn = SEG, convexity = 10) polygon(pts); }

module louver_ring(r) {
    a = r[0]; b = r[1]; c = r[2]; d = r[3];
    revolve(concat(flare(d, b), [[b - ring_edge, H], [a + ring_edge, H]], rev(flare(c, a))));
}

module sector(a0, a1) {
    translate([0, 0, -2]) linear_extrude(H + 4)
        polygon(concat([[0, 0]], [for (i = [0 : 39]) let (t = a0 + (a1 - a0) * i / 39) [R * 1.3 * cos(t), R * 1.3 * sin(t)]]));
}

module scoop_ellipsoid(angle, grow = 0) {
    rotate([0, 0, angle]) translate([scoop_r, 0, 0.608 * H]) rotate([0, -scoop_tilt, 0])
        scale([scoop_len + grow, scoop_wid + grow, scoop_dep + grow])
            sphere(r = 1, $fn = SEG_SMALL);
}

module scoop_cutter(angle) {
    hull() {
        scoop_ellipsoid(angle);
        translate([0, 0, 12]) scoop_ellipsoid(angle);
    }
}

module scoop_dome(angle) {
    intersection() {
        scoop_ellipsoid(angle, scoop_shell);
        revolve([[spigot_rim_in + 0.3, 0], [R - 0.6, 0], [R - 0.6, Z_FB + 0.5], [spigot_rim_in + 1.6, Z_FB + 0.5]]);
    }
}

module outer_body() {
    revolve(body_profile());
    if (show_scoops) for (k = [0, 180]) scoop_dome(scoop_angle + k);
    for (i = [0 : 1 : rib_count - 1])
        rotate([0, 0, rib_start + i * 360 / rib_count])
            translate([spigot_rim_out - 0.2, -rib_t / 2, 0.3]) cube([rib_len, rib_t, Z_FB - 0.3]);
    for (i = [0 : 1 : pad_count - 1]) let (a0 = pad_start + i * 360 / pad_count)
        intersection() {
            revolve([[spigot_rim_out - 0.5, 0], [pad_r, 0], [pad_r, pad_h],
                     [pad_r - 0.5, pad_h + 0.8], [spigot_rim_out - 0.5, pad_h + 0.8]]);
            sector(a0, a0 + pad_span);
        }
}

module rings() {
    last = len(RINGS) - 1;
    for (i = [0 : last - 1]) louver_ring(RINGS[i]);
    difference() {
        louver_ring(RINGS[last]);
        if (show_scoops) for (k = [0, 180])
            rotate([0, 0, scoop_angle + k]) translate([notch_r, 0, -2])
                scale([notch_sr, notch_st, 1]) cylinder(h = H + 4, r = 1, $fn = 96);
    }
}

module spokes() {
    intersection() {
        for (a = [0, 90]) rotate([0, 0, a]) rotate([90, 0, 90])
            linear_extrude(height = outer_d, center = true)
                polygon([[-spoke_w_back / 2, 0], [spoke_w_back / 2, 0],
                         [spoke_w_front / 2, H], [-spoke_w_front / 2, H]]);
        revolve([[spoke_r_in, 0], [spigot_rim_out - 0.8, 0], [spigot_rim_out + 0.4, 0.5 * H],
                 [flange_in_r + 0.4, H], [spoke_r_in, H]]);
    }
}

module pin_pads() {
    if (show_pin_pads)
        for (rr = concat([for (r = RINGS) (r[2] + r[3]) / 2], [(spigot_rim_in + spigot_rim_out) / 2]))
            for (a = [0, 90, 180, 270])
                rotate([0, 0, a]) translate([rr, 0, 0]) cylinder(h = pin_pad_t, r = pin_pad_r, $fn = 24);
}

module tabs() {
    if (show_tabs)
        for (a = [0, 180]) rotate([0, 0, a])
            intersection() {
                translate([spigot_rim_in - 0.1, -tab_w / 2, 0])
                    cube([tab_r_end - spigot_rim_in + 0.1, tab_w, tab_t]);
                cylinder(h = tab_t, r = tab_r_end, $fn = SEG);
            }
}

module grille() {
    difference() {
        union() {
            outer_body();
            rings();
            pin_pads();
            tabs();
            revolve(hub_profile());
            spokes();
        }
        if (show_scoops) for (k = [0, 180]) scoop_cutter(scoop_angle + k);
        revolve(bore_profile());
    }
}

if (print_orientation)
    translate([0, 0, H]) rotate([180, 0, 0]) grille();
else
    grille();
