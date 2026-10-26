"""Generate visual 3D exploded & cutaway assembly guides for all models."""

from __future__ import annotations

import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh

MODELS_DIR = Path(r"<WORKSPACE_ROOT>\models")
ART_DIR = Path(r"<APP_DATA_DIR>\brain\810bc3d9-16ad-400e-a0b4-e2ed588c9701")

light_dir = np.array([0.45, -0.55, 0.70])
light_dir /= np.linalg.norm(light_dir)


def add_mesh(ax, m: trimesh.Trimesh, color_rgb: np.ndarray, alpha: float = 1.0, edge_alpha: float = 0.15, max_edge: float = 16.0, zorder: int = 2) -> None:
    v_s, f_s = trimesh.remesh.subdivide_to_size(m.vertices, m.faces, max_edge=max_edge)
    sm = trimesh.Trimesh(vertices=v_s, faces=f_s, process=False)
    tris = sm.vertices[sm.faces]
    norms = sm.face_normals
    intens = np.clip(0.35 + 0.65 * np.abs(np.dot(norms, light_dir)), 0.2, 1.0)
    fcols = np.zeros((len(tris), 4))
    fcols[:, :3] = np.clip(np.outer(intens, color_rgb), 0, 1)
    fcols[:, 3] = alpha
    ec = (0.08, 0.10, 0.14, edge_alpha) if alpha > 0.5 else (0.2, 0.3, 0.4, 0.08)
    poly = Poly3DCollection(tris, facecolors=fcols, edgecolors=ec, linewidths=0.08, zorder=zorder)
    ax.add_collection3d(poly)


def add_badge(ax, x2d: float, y2d: float, text: str, border_col: str) -> None:
    ax.text2D(
        x2d,
        y2d,
        text,
        transform=ax.transAxes,
        color="#f0f4f8",
        fontsize=8.5,
        fontweight="bold",
        zorder=100,
        bbox=dict(
            facecolor="#11151c",
            alpha=0.94,
            edgecolor=border_col,
            linewidth=1.5,
            boxstyle="round,pad=0.45",
        ),
    )


def render_planter_assembly_guide() -> Path:
    base_dir = MODELS_DIR / "cherry-tomato-modular-planter" / "exports"
    base_mesh = trimesh.load_mesh(str(base_dir / "cherry_tomato_modular_planter_tray1_base_6color.stl"))
    saucer_mesh = trimesh.load_mesh(str(base_dir / "cherry_tomato_modular_planter_tray2_saucer_1color.stl"))
    riser_mesh = trimesh.load_mesh(str(base_dir / "cherry_tomato_modular_planter_tray3_riser_4color.stl"))
    straw_pair = trimesh.load_mesh(str(base_dir / "cherry_tomato_modular_planter_tray4_irrigation_straws_2color.stl"))

    parts_straw = straw_pair.split(only_watertight=False)
    single_straw_parts = [p for p in parts_straw if p.bounds[:, 1].mean() > 0]
    single_straw = trimesh.util.concatenate(single_straw_parts)
    single_straw.apply_translation([0.0, -5.0, -5.3])

    fig = plt.figure(figsize=(18, 7.2), dpi=160, facecolor="#11151c")

    # PANEL 1: Step 1 (Thread cotton strip/rope inside arch straw)
    ax1 = fig.add_subplot(1, 3, 1, projection="3d", facecolor="#161b24", computed_zorder=False)
    straw_flat = single_straw.copy()
    straw_flat.apply_translation([0, 0, 5.3])
    add_mesh(ax1, straw_flat, np.array([0.85, 0.55, 0.25]), alpha=0.88, max_edge=8.0, zorder=2)

    t_vals = np.linspace(0, np.pi, 60)
    wick_x = np.concatenate([[-64.0, -64.0], -64.0 * np.cos(t_vals), [64.0, 64.0]])
    wick_y = np.concatenate([[-28.0, 46.0], 46.0 + 64.0 * np.sin(t_vals), [46.0, -28.0]])
    wick_z = np.full_like(wick_x, 5.3)
    ax1.plot(wick_x, wick_y, wick_z, color="#4cc9f0", linewidth=4.5, zorder=10)
    ax1.scatter([-64.0, 64.0], [-25.0, -25.0], [5.3, 5.3], color="#4cc9f0", s=50, zorder=11)
    add_badge(ax1, 0.03, 0.85, "15x Root-Watering Slits along Top Arch\nRoots drink moisture from wet cloth inside", "#ffd166")
    add_badge(ax1, 0.03, 0.04, "Cyan Line = 35 cm Cotton T-Shirt Strip / Wick Rope\nLeave 3 cm hanging out of both Ø7.4mm bottom plugs", "#4cc9f0")
    ax1.set_xlim(-95, 95)
    ax1.set_ylim(-45, 125)
    ax1.set_zlim(-15, 35)
    ax1.set_box_aspect([190, 170, 50])
    ax1.view_init(elev=32, azim=-60)
    ax1.set_title("STEP 1: Thread Cotton Cloth / Rope Inside Straw\n(Before adding soil)", color="#f0f4f8", fontsize=10.5, fontweight="bold", pad=8)

    # PANEL 2: Step 2 (Plug 2 arches upright into floor holes)
    ax2 = fig.add_subplot(1, 3, 2, projection="3d", facecolor="#161b24", computed_zorder=False)
    rot_x90 = trimesh.transformations.rotation_matrix(np.pi / 2.0, [1, 0, 0])
    straw_up1 = single_straw.copy()
    straw_up1.apply_transform(rot_x90)
    saucer_pos = saucer_mesh.copy()
    base_pos = base_mesh.copy().apply_translation([0, 0, 10.0])

    add_mesh(ax2, saucer_pos, np.array([0.20, 0.48, 0.68]), alpha=0.85, max_edge=20.0, zorder=1)
    for dy_row in (-42.0, 42.0):
        st = straw_up1.copy()
        st.apply_translation([0.0, dy_row, 15.0 - 16.0])
        add_mesh(ax2, st, np.array([0.92, 0.58, 0.22]), alpha=1.0, max_edge=10.0, zorder=4)
        wz = np.concatenate([[-24.0, 46.0], 46.0 + 64.0 * np.sin(t_vals), [46.0, -24.0]]) + (15.0 - 16.0)
        wy = np.full_like(wick_x, dy_row)
        ax2.plot(wick_x, wy, wz, color="#4cc9f0", linewidth=3.2, zorder=5)
    add_mesh(ax2, base_pos, np.array([0.22, 0.62, 0.45]), alpha=0.18, edge_alpha=0.04, max_edge=22.0, zorder=6)

    add_badge(ax2, 0.03, 0.85, "2x Standing Arch Straws (X = -64 & +64 mm)\nStand upright like rainbows inside potting soil", "#ffd166")
    add_badge(ax2, 0.03, 0.04, "Bottom Plugs & Cloth Tails Poke Through Floor\nDip directly into Drip Saucer water reservoir!", "#4cc9f0")
    ax2.set_xlim(-130, 130)
    ax2.set_ylim(-110, 110)
    ax2.set_zlim(0, 210)
    ax2.set_box_aspect([260, 220, 210])
    ax2.view_init(elev=22, azim=-52)
    ax2.set_title("STEP 2: Plug 2 Arches Upright into Floor Holes\n(X-Ray Cutaway View)", color="#f0f4f8", fontsize=10.5, fontweight="bold", pad=8)

    # PANEL 3: Step 3 & 4 (Stack Riser & Insert Rods)
    ax3 = fig.add_subplot(1, 3, 3, projection="3d", facecolor="#161b24", computed_zorder=False)
    add_mesh(ax3, saucer_pos, np.array([0.18, 0.45, 0.35]), alpha=0.95, max_edge=22.0, zorder=1)
    add_mesh(ax3, base_pos, np.array([0.25, 0.65, 0.48]), alpha=0.92, max_edge=22.0, zorder=2)

    riser_flipped = riser_mesh.copy()
    rot_x180 = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
    riser_flipped.apply_transform(rot_x180)
    riser_flipped.apply_translation([0, 0, 390.0])
    add_mesh(ax3, riser_flipped, np.array([0.82, 0.52, 0.24]), alpha=0.95, max_edge=22.0, zorder=4)

    for cx, cy in [(-103, -78), (103, -78), (103, 78), (-103, 78)]:
        ax3.plot([cx, cx], [cy, cy], [205, 430], "--", color="#ffd166", linewidth=2.0, zorder=5)

    add_badge(ax3, 0.03, 0.85, "Tray 3 Extension Riser (Flipped 180° Right-Side-Up)\n4 integrated corner pins lock into Base corner holes", "#ffd166")
    add_badge(ax3, 0.03, 0.04, "4x Corner Trellis Sockets (Ø6.5mm / Ø4.5mm)\nInsert 4mm or 6mm metal stakes/strings for tomatoes", "#52B788")
    ax3.set_xlim(-135, 135)
    ax3.set_ylim(-110, 110)
    ax3.set_zlim(0, 420)
    ax3.set_box_aspect([270, 220, 340])
    ax3.view_init(elev=20, azim=-48)
    ax3.set_title("STEP 3 & 4: Fill Soil, Stack Riser & Insert Rods\n(Exploded Stacking View)", color="#f0f4f8", fontsize=10.5, fontweight="bold", pad=8)

    for a in (ax1, ax2, ax3):
        a.tick_params(colors="#7b8794", labelsize=7)
        a.xaxis.pane.fill = False
        a.yaxis.pane.fill = False
        a.zaxis.pane.fill = False

    plt.tight_layout()
    out_planter_guide = MODELS_DIR / "cherry-tomato-modular-planter" / "previews" / "assembly_and_straw_guide.png"
    fig.savefig(str(out_planter_guide), dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)

    shutil.copy2(out_planter_guide, ART_DIR / "assembly_and_straw_guide.png")
    for p_folder in [
        "01-oval-stadium-planter",
        "02-roman-fluted-column-planter",
        "03-origami-faceted-prism-planter",
        "04-self-watering-sip-wicking-planter",
        "05-hexagonal-honeycomb-tessellation-planter",
        "06-zen-stepped-pagoda-wave-planter",
    ]:
        shutil.copy2(out_planter_guide, MODELS_DIR / p_folder / "previews" / "assembly_and_straw_guide.png")
    return out_planter_guide


def render_melitta_assembly_guide() -> Path:
    mel_dir = MODELS_DIR / "melitta-coffee-bean-dispenser" / "exports"
    m_box = trimesh.load_mesh(str(mel_dir / "Melitta_Bean_Hopper_Box_60mm.stl"))
    m_shutter = trimesh.load_mesh(str(mel_dir / "Rotary_Shutter_Geared_Thumbwheel_30mm.stl"))
    m_ramp = trimesh.load_mesh(str(mel_dir / "Internal_Sloped_Bean_Ramp.stl"))

    m_box_c = m_box.copy().apply_translation([41.5, 17.0, 0.0])
    m_shutter_c = m_shutter.copy().apply_translation([-23.5 - 39.0, 17.5 - 2.0, 72.0])
    m_ramp_c = m_ramp.copy().apply_translation([-53.5, -28.5, 110.0])

    fig2 = plt.figure(figsize=(12.5, 7.2), dpi=160, facecolor="#11151c")
    axm = fig2.add_subplot(1, 1, 1, projection="3d", facecolor="#161b24", computed_zorder=False)
    add_mesh(axm, m_box_c, np.array([0.22, 0.65, 0.48]), alpha=0.82, max_edge=14.0, zorder=1)
    add_mesh(axm, m_shutter_c, np.array([0.92, 0.58, 0.22]), alpha=0.98, max_edge=10.0, zorder=3)
    add_mesh(axm, m_ramp_c, np.array([0.32, 0.55, 0.85]), alpha=0.92, max_edge=14.0, zorder=5)

    axm.plot([-39, -39], [15.5, 15.5], [8, 72], "--", color="#ffd166", linewidth=2.2, zorder=6)
    axm.plot([0, 0], [20, 20], [15, 110], "--", color="#4cc9f0", linewidth=2.2, zorder=6)

    add_badge(axm, 0.03, 0.83, "STEP 2 (Top Blue): Internal_Sloped_Bean_Ramp\n• Flip right-side-up & glue stationary perimeter inside box\n• Bottom pin seats into floor hole & holds shutter captive", "#4cc9f0")
    add_badge(axm, 0.03, 0.65, "STEP 1 (Middle Gold): Rotary_Shutter_Geared_Thumbwheel_30mm\n• Lower Ø4mm hole onto floor pivot pin (Z = 5 mm)\n• 17-tooth geared Ø30mm wheel protrudes through side slot", "#ffd166")
    add_badge(axm, 0.03, 0.04, "BASE (Bottom Green): Melitta_Bean_Hopper_Box_60mm (60.0 mm Height)\n• STEP 3: Pop your original Melitta clear window lid into top 5mm step (Z = 55..60 mm)", "#52B788")

    axm.set_xlim(-75, 75)
    axm.set_ylim(-90, 90)
    axm.set_zlim(0, 155)
    axm.set_box_aspect([150, 180, 145])
    axm.view_init(elev=24, azim=-50)
    axm.set_title("Melitta 60 mm Bean Dispenser — Step-by-Step Exploded Assembly Guide", color="#f0f4f8", fontsize=12, fontweight="bold", pad=10)
    axm.tick_params(colors="#7b8794", labelsize=7)
    axm.xaxis.pane.fill = False
    axm.yaxis.pane.fill = False
    axm.zaxis.pane.fill = False
    plt.tight_layout()

    out_mel_guide = MODELS_DIR / "melitta-coffee-bean-dispenser" / "previews" / "melitta_assembly_guide.png"
    fig2.savefig(str(out_mel_guide), dpi=160, facecolor=fig2.get_facecolor())
    plt.close(fig2)
    shutil.copy2(out_mel_guide, ART_DIR / "melitta_assembly_guide.png")
    return out_mel_guide


if __name__ == "__main__":
    p1 = render_planter_assembly_guide()
    p2 = render_melitta_assembly_guide()
    print(f"Rendered: {p1} and {p2}")
