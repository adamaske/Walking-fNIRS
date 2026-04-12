import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

import cedalion
import cedalion.vis.anatomy
import cedalion.io.snirf as snirf_io

import cedalion.nirs.cw as cw
import cedalion.sigproc.frequency as frequency
import cedalion.vis.colors as colors

import cedalion.sigproc.motion as motion
import cedalion.sigproc.quality as quality
from cedalion.vis.quality import plot_quality_mask

from cedalion import units

xr.set_options(display_expand_data=False)

walking_path = "data/sub01/walking.snirf"
sitting_path = "data/sub01/sitting.snirf"
walking_path = "data/sub01/walking_cont.snirf"
walking_block_path = "data/sub01/walking_block.snirf"

perc_time_clean_threshold = 0.75

sci_threshold = 0.75
psp_threshold = 0.03

sci_norm, sci_cmap = colors.threshold_cmap("sci_cmap", 0.0, 1.0, sci_threshold)
psp_norm, psp_cmap = colors.threshold_cmap("psp_cmap", 0.0, 0.30, psp_threshold)

window_length = 10 * units.s

# Bandpass filter
bp_low = 0.01 * units.Hz
bp_high = 0.2 * units.Hz
bp_order = 5


def plot_sci(sci):
    # plot the heatmap
    f, ax = plt.subplots(1, 1, figsize=(12, 10))

    m = ax.pcolormesh(
        sci.time,
        np.arange(len(sci.channel)),
        sci,
        shading="nearest",
        cmap=sci_cmap,
        norm=sci_norm,
    )
    cb = plt.colorbar(m, ax=ax)
    cb.set_label("SCI")
    ax.set_xlabel("time / s")
    plt.tight_layout()
    ax.yaxis.set_ticks(np.arange(len(sci.channel)))
    ax.yaxis.set_ticklabels(sci.channel.values, fontsize=7)


def plot_psp(psp):
    f, ax = plt.subplots(1, 1, figsize=(12, 10))

    m = ax.pcolormesh(
        psp.time,
        np.arange(len(psp.channel)),
        psp,
        shading="nearest",
        cmap=psp_cmap,
        norm=psp_norm,
    )
    cb = plt.colorbar(m, ax=ax)
    cb.set_label("PSP")
    ax.set_xlabel("time / s")
    plt.tight_layout()
    ax.yaxis.set_ticks(np.arange(len(psp.channel)))
    ax.yaxis.set_ticklabels(psp.channel.values, fontsize=7)


def analyze_rec(filepath, visualize_correction=True):
    print(f"====Analyzing : {filepath}")
    rec = snirf_io.read_snirf(filepath)[0]

    print(f"====Stim====")
    rec.stim.cd.rename_events(
        {
            "1": "standing_start",
            "2": "standing_end",
            "3": "walking_start",
            "4": "walking_end",
        }
    )
    print(rec.stim)

    print(f"====Signal Quality====")

    sci, sci_mask = quality.sci(rec["amp"], window_length, sci_threshold)
    psp, psp_mask = quality.psp(rec["amp"], window_length, psp_threshold)

    combined_mask = sci_mask & psp_mask

    perc_time_clean = combined_mask.sum(dim="time") / len(sci.time)
    print(perc_time_clean)
    print(perc_time_clean[perc_time_clean < perc_time_clean_threshold])

    rec["od"] = cw.int2od(rec["amp"])
    rec["od_corrected"] = motion.tddr(rec["od"])
    rec["od_corrected"] = motion.wavelet(rec["od_corrected"])
    rec["amp_corrected"] = cw.od2int(rec["od_corrected"], rec["amp"].mean("time"))

    sci_corr, sci_corr_mask = quality.sci(
        rec["amp_corrected"], window_length, sci_threshold
    )
    psp_corr, psp_corr_mask = quality.psp(
        rec["amp_corrected"], window_length, psp_threshold
    )

    combined_corr_mask = sci_corr_mask & psp_corr_mask
    perc_time_clean_corr = combined_corr_mask.sum(dim="time") / len(sci_corr.time)

    if visualize_correction:
        # |----------|-----------|
        # |  CM-pre  |  CM-post  |
        # |----------|-----------|
        # | Scalp-pre| Scalp-post|
        # |----------|-----------|
        fig, axes = plt.subplots(2, 2, figsize=(16, 14))
        fig.suptitle(filepath)

        mask_norm, mask_cmap = colors.mask_cmap(True)

        def _draw_mask(ax, mask, title):
            m = ax.pcolormesh(
                mask.time,
                np.arange(len(mask.channel)),
                mask,
                shading="nearest",
                norm=mask_norm,
                cmap=mask_cmap,
            )
            cb = plt.colorbar(m, ax=ax)
            cb.set_label("combined mask")
            cb.set_ticks([0.25, 0.75])
            cb.set_ticklabels(["TAINTED", "CLEAN"])
            ax.set_xlabel("time / s")
            ax.yaxis.set_ticks(np.arange(len(mask.channel)))
            ax.yaxis.set_ticklabels(mask.channel.values, fontsize=6)
            ax.set_title(title)

        _draw_mask(axes[0, 0], combined_mask, "Combined mask (pre-correction)")
        _draw_mask(axes[0, 1], combined_corr_mask, "Combined mask (post-correction)")

        cedalion.vis.anatomy.scalp_plot(
            rec["amp"],
            rec.geo3d,
            perc_time_clean,
            axes[1, 0],
            cmap="RdYlGn",
            vmin=0.5,
            vmax=1,
            title="Percentage of clean time (pre-correction)",
            cb_label="Percentage of clean time",
            channel_lw=2,
            optode_labels=True,
        )

        cedalion.vis.anatomy.scalp_plot(
            rec["amp_corrected"],
            rec.geo3d,
            perc_time_clean_corr,
            axes[1, 1],
            cmap="RdYlGn",
            vmin=0.5,
            vmax=1,
            title="Percentage of clean time (post-correction)",
            cb_label="Percentage of clean time",
            channel_lw=2,
            optode_labels=True,
        )

        fig.tight_layout()
        plt.show()
        return
    print("====Temporal Filtering====")
    rec["od_corrected_filtered"] = frequency.freq_filter(
        rec["od_corrected"], bp_low, bp_high
    )
    rec["od_filtered"] = frequency.freq_filter(rec["od"], bp_low, bp_high)
    print(f"Applied bandpass filter: [ {bp_low}, {bp_high}]")

    print("====Wavelengths====")
    wls = rec["amp"].wavelength.values
    print(wls)

    print("====MBLL====")
    dpf_factor = 6.0
    dpf = xr.DataArray(
        [dpf_factor] * len(wls),
        dims=["wavelength"],
        coords={"wavelength": wls},
    )
    rec["conc"] = cw.od2conc(rec["od"], rec.geo3d, dpf)
    rec["conc_filtered"] = cw.od2conc(rec["od_filtered"], rec.geo3d, dpf)
    rec["conc_corrected"] = cw.od2conc(rec["od_corrected"], rec.geo3d, dpf)
    rec["conc_corrected_filtered"] = cw.od2conc(
        rec["od_corrected_filtered"], rec.geo3d, dpf
    )
    print(f"====Output====")
    stem, ext = filepath.rsplit(".", 1)
    output_name = f"{stem}_corrected.{ext}"
    snirf_io.write_snirf(output_name, rec)
    print(f"Wrote .snirf: {output_name}")


# analyze_rec(sitting_path, True)
# analyze_rec(walking_path, True)
# analyze_rec(walking_path, True)
analyze_rec(walking_block_path, False)
