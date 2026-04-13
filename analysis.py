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

t_motion = 0.5 * units.s  # motion artifact detection time window
t_mask = 1.0 * units.s  # masking motion artifacts time window
# (+- t_mask s before/after detected motion artifact)
stdev_thresh = 7.0  # Deviation of the signal to detect motion artifact.
# 50.0 is default, 7.0 is very low
amp_thresh = 5.0  # Amplitude threshold to detect motion articats
# Default is 5.0
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


def signal_quality_analysis(uncorrected, corrected=None, geo3d=None, plot=False):
    sci, sci_mask = quality.sci(uncorrected, window_length, sci_threshold)
    psp, psp_mask = quality.psp(uncorrected, window_length, psp_threshold)
    combined_mask = sci_mask & psp_mask
    perc_time_clean = combined_mask.sum(dim="time") / len(sci.time)
    gvtd, gvtd_mask = quality.gvtd(uncorrected)

    if corrected is not None:
        sci_corr, sci_corr_mask = quality.sci(corrected, window_length, sci_threshold)
        psp_corr, psp_corr_mask = quality.psp(corrected, window_length, psp_threshold)
        combined_corr_mask = sci_corr_mask & psp_corr_mask
        perc_time_clean_corr = combined_corr_mask.sum(dim="time") / len(sci_corr.time)
        gvtd_corr, gvtd_corr_mask = quality.gvtd(corrected)
        improved_windows = (combined_mask == quality.TAINTED) & (
            combined_corr_mask == quality.CLEAN
        )
        worsened_windows = (combined_mask == quality.CLEAN) & (
            combined_corr_mask == quality.TAINTED
        )

    if plot:
        has_corrected = corrected is not None
        nrows = 2 if has_corrected else 1
        # Columns: scalp, combined mask, [improved/worsened if corrected], GVTD
        ncols = 4 if has_corrected else 3
        fig, axes = plt.subplots(nrows, ncols, figsize=(8 * ncols, 7 * nrows))
        if nrows == 1:
            axes = axes[np.newaxis, :]

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

        def _draw_change_mask(ax, mask, title, cmap):
            m = ax.pcolormesh(
                mask.time,
                np.arange(len(mask.channel)),
                mask.astype(int),
                shading="nearest",
                cmap=cmap,
                vmin=0,
                vmax=1,
            )
            cb = plt.colorbar(m, ax=ax)
            cb.set_ticks([0, 1])
            cb.set_ticklabels(["No", "Yes"])
            ax.set_xlabel("time / s")
            ax.yaxis.set_ticks(np.arange(len(mask.channel)))
            ax.yaxis.set_ticklabels(mask.channel.values, fontsize=6)
            ax.set_title(title)

        def _draw_gvtd(ax, gvtd, gvtd_mask, title):
            ax.plot(gvtd.time, gvtd, color="steelblue", linewidth=0.8)
            ax.set_xlabel("time / s")
            ax.set_ylabel("GVTD")
            ax.set_title(title)
            for i in range(len(gvtd_mask.time)):
                t0 = float(gvtd_mask.time.values[i])
                t1 = (
                    float(gvtd_mask.time.values[i + 1])
                    if i + 1 < len(gvtd_mask.time)
                    else float(gvtd.time.values[-1])
                )
                color = "red" if gvtd_mask.isel(time=i) == quality.TAINTED else "green"
                ax.axvspan(t0, t1, alpha=0.15, color=color)

        # Column 1: Scalp plots
        scalp_kwargs = dict(
            cmap="RdYlGn",
            vmin=0.5,
            vmax=1,
            cb_label="Percentage of clean time",
            channel_lw=2,
            optode_labels=True,
        )
        if geo3d is not None:
            cedalion.vis.anatomy.scalp_plot(
                uncorrected,
                geo3d,
                perc_time_clean,
                axes[0, 0],
                title="% clean time (pre-correction)",
                **scalp_kwargs,
            )
            if has_corrected:
                cedalion.vis.anatomy.scalp_plot(
                    corrected,
                    geo3d,
                    perc_time_clean_corr,
                    axes[1, 0],
                    title="% clean time (post-correction)",
                    **scalp_kwargs,
                )
        else:
            axes[0, 0].set_visible(False)
            if has_corrected:
                axes[1, 0].set_visible(False)

        # Column 2: Combined masks
        _draw_mask(axes[0, 1], combined_mask, "Combined mask (pre-correction)")
        if has_corrected:
            _draw_mask(
                axes[1, 1], combined_corr_mask, "Combined mask (post-correction)"
            )

        if has_corrected:
            # Column 3: Improved / Worsened windows
            _draw_change_mask(
                axes[0, 2], improved_windows, "Windows improved by correction", "Greens"
            )
            _draw_change_mask(
                axes[1, 2], worsened_windows, "Windows worsened by correction", "Reds"
            )
            # Column 4: GVTD
            _draw_gvtd(axes[0, 3], gvtd, gvtd_mask, "GVTD (pre-correction)")
            _draw_gvtd(axes[1, 3], gvtd_corr, gvtd_corr_mask, "GVTD (post-correction)")
        else:
            # Column 3: GVTD (no corrected → no change mask column)
            _draw_gvtd(axes[0, 2], gvtd, gvtd_mask, "GVTD")

        fig.tight_layout()
        plt.show()

    return combined_mask, perc_time_clean


def motion_artifact_detection(fnirs_data, channels, plot: False):
    ma_mask = quality.id_motion(fnirs_data, t_motion, t_mask, stdev_thresh, amp_thresh)
    if plot:
        # Figure subplots, a square grid based on len(example_channels),
        # 1 or 2 elements gets a single row, after that a square grid
        n = len(channels)
        if n <= 2:
            nrows, ncols = 1, n
        else:
            ncols = int(np.ceil(np.sqrt(n)))
            nrows = int(np.ceil(n / ncols))

            fig, axes = plt.subplots(
                nrows, ncols, figsize=(8 * ncols, 4 * nrows), squeeze=False
            )
            axes_flat = axes.flat

            for ax, example in zip(axes_flat, channels):
                ax.plot(
                    ma_mask.time,
                    ma_mask.sel(channel=example, wavelength="760"),
                    "b-",
                    label="760nm",
                )
                ax.plot(
                    ma_mask.time,
                    ma_mask.sel(channel=example, wavelength="850"),
                    "r-",
                    label="850nm",
                )

                ax.plot(
                    fnirs_data.time,
                    fnirs_data.sel(channel=example, wavelength="760"),
                    "b--",
                    label="HbR",
                )
                ax.plot(
                    fnirs_data.time,
                    fnirs_data.sel(channel=example, wavelength="850"),
                    "r--",
                    label="HbO",
                )
                #  TODO:    Add the "walking_start" and "walking_end" markers
                #           from events as vertical lines in the plots
                ax.set_xlabel("time / s")
                ax.set_ylabel("Motion artifact mask")
                ax.set_title(example)
                ax.legend()

            # Hide any unused axes
            for ax in list(axes_flat)[n:]:
                ax.set_visible(False)

        fig.tight_layout()
    return ma_mask


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

    print(f"====Optical Density====")
    rec["od"] = cw.int2od(rec["amp"])

    # Correcting with TDDR and Wavelet
    rec["od_corrected"] = motion.tddr(rec["od"])
    rec["od_corrected"] = motion.wavelet(rec["od_corrected"])
    rec["amp_corrected"] = cw.od2int(rec["od_corrected"], rec["amp"].mean("time"))

    print(f"====Signal Quality====")
    signal_quality_analysis(
        rec["amp"],
        corrected=rec["amp_corrected"],
        geo3d=rec.geo3d,
        plot=visualize_correction,
    )

    print(f"====Motion Artifact Detection====")
    # Plotting the detcted intervals with the channel
    example_channels = ["S9D9", "S3D2", "S12D7", "S13D12", "S11D10", "S1D1"]
    ma_mask = motion_artifact_detection(rec["od"], example_channels, plot=True)
    plt.show()
    print(f"====Motion Correction====")
    # 1. SplineSG
    # 2. TDDR
    # 3. PCA
    # 4. Recursive PCA
    # 5. Wavelet Motion Correction
    # 6. TDDR
    # 7. Wavelet
    # 8. Combined TDDR & Wavelet

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
analyze_rec(walking_block_path, True)
