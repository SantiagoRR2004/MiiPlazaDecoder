from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import tkinter.font as tkfont
import tkinter as tk
import pandas as pd
import numpy as np
import itertools
import sys


class Grapher:
    def _get_best_font(self) -> str:
        """
        Get the best available font that supports CJK characters

        Args:
            - None

        Returns:
            str: Font name that supports CJK characters
        """
        # List of fonts that typically support CJK characters
        cjk_fonts = [
            "Noto Sans CJK JP",
            "Noto Sans CJK SC",
            "Noto Sans CJK TC",
            "Noto Sans CJK KR",
            "SimSun",
            "Microsoft YaHei",
            "Malgun Gothic",
            "Yu Gothic",
            "Hiragino Sans",
            "Apple SD Gothic Neo",
            "Source Han Sans",
            "WenQuanYi Micro Hei",
            "Droid Sans Fallback",
            "Arial Unicode MS",
        ]

        # Get list of available fonts
        available_fonts = [f.name for f in fm.fontManager.ttflist]

        # Find the first available CJK font
        for font in cjk_fonts:
            if font in available_fonts:
                return font

        # If no CJK font is found, return a fallback
        return "DejaVu Sans"

    def graphPieChartTkinter(self, data: pd.Series) -> None:

        valueCounts = data.value_counts().reset_index()
        valueCounts.columns = [data.name, "count"]

        # Sort by count (descending) and then by value (ascending)
        valueCounts = valueCounts.sort_values(
            by=["count", data.name], ascending=[False, True]
        )

        labels = valueCounts[data.name].values
        sizes = valueCounts["count"].values
        total = sum(sizes)

        def on_closing():
            plt.close("all")
            root.destroy()
            sys.exit()

        threshold = 2

        def autopct_format(pct):
            return f"{pct:.1f}%" if pct >= threshold else ""

        final_labels = [
            label if (size / total * 100) >= threshold else ""
            for label, size in zip(labels, sizes)
        ]

        # Get best font for CJK support
        best_font = self._get_best_font()

        colorCycle = itertools.cycle(plt.cm.tab10.colors)

        # Get the colors
        colorMap = {
            size: next(colorCycle)
            for size in sorted({int(s) for s in sizes}, reverse=True)
        }
        wedgeColors = [colorMap[int(size)] for size in sizes]

        # Plot figure
        fig, ax = plt.subplots(figsize=(6, 6))

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=final_labels,
            autopct=autopct_format,
            startangle=0,
            shadow=False,
            textprops={"fontname": best_font},
            colors=wedgeColors,
        )

        # Calculate cumulative angles for boundaries between wedges
        cumulative = np.cumsum([0] + sizes) / total * 360

        # Draw black lines between wedges (edges)
        for i in range(len(sizes)):
            if sizes[i] != sizes[(i + 1) % len(sizes)]:
                angle = cumulative[i]  # boundary after wedge i
                theta = np.deg2rad(angle)
                r = 1
                ax.plot(
                    [0, r * np.cos(theta)],
                    [0, r * np.sin(theta)],
                    color="black",
                    linewidth=1.5,
                )

        # Add a black circular border around the pie chart
        circle = Circle((0, 0), 1, edgecolor="black", facecolor="none", linewidth=1.5)
        ax.add_patch(circle)

        ax.set_title(f"Distribution of {data.name}")
        ax.set_aspect("equal")

        # Tkinter window
        root = tk.Tk()
        root.geometry("400x400")
        root.wm_title("Scrollable Legend Pie Chart")
        root.protocol("WM_DELETE_WINDOW", on_closing)

        # Create hidden window to measure content
        hidden_win = tk.Toplevel(root)
        hidden_win.withdraw()  # Hide it

        # Find widest label and size
        test_font = tkfont.Font(family=best_font, size=9)
        max_label_width = max(test_font.measure(label) for label in labels)
        max_size_width = max(test_font.measure(str(size)) for size in sizes)

        needed_width = (
            max_label_width + max_size_width + (4 * 10)
        )  # Add padding manually

        # Matplotlib canvas
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Container frame for centering the legend
        container_frame = tk.Frame(root)
        container_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Left spacer for centering
        left_spacer = tk.Frame(container_frame, bg="white")
        left_spacer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame for scrollbar and legend text (fixed width)
        frame = tk.Frame(container_frame, width=needed_width, bg="white")
        frame.pack(side=tk.LEFT, fill=tk.Y)
        frame.pack_propagate(False)  # Maintain fixed width

        # Top spacer for vertical centering
        top_spacer = tk.Frame(frame, bg="white")
        top_spacer.pack(side=tk.TOP, fill=tk.X, expand=True)

        # Middle frame to hold the actual legend content
        legend_frame = tk.Frame(frame)
        legend_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Bottom spacer for vertical centering
        bottom_spacer = tk.Frame(frame, bg="white")
        bottom_spacer.pack(side=tk.BOTTOM, fill=tk.X, expand=True)

        # Right spacer for centering
        right_spacer = tk.Frame(container_frame, bg="white")
        right_spacer.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create a scrollbar and a canvas to hold the legend labels
        scrollbar = tk.Scrollbar(legend_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        legend_canvas = tk.Canvas(
            legend_frame, width=needed_width, yscrollcommand=scrollbar.set
        )
        legend_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=legend_canvas.yview)

        # Create a frame inside the canvas to hold labels
        labels_frame = tk.Frame(legend_canvas)
        canvas_window = legend_canvas.create_window(
            (0, 0), window=labels_frame, anchor="nw"
        )

        # Add legend entries as labels inside labels_frame
        for idx, (label, size) in enumerate(zip(labels, sizes)):
            # Convert matplotlib color to hex for tkinter
            color = wedgeColors[idx]
            hex_color = f"#{int(color[0]*255):02x}{int(color[1]*255):02x}{int(color[2]*255):02x}"

            # Create a colored frame for the entire row
            row_frame = tk.Frame(labels_frame, bg=hex_color)
            row_frame.grid(row=idx, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, weight=1)

            lbl_label = tk.Label(
                row_frame, text=label, font=(best_font, 9), anchor="w", bg=hex_color
            )
            lbl_size = tk.Label(
                row_frame,
                text=str(size),
                font=(best_font, 9),
                anchor="e",
                bg=hex_color,
            )
            lbl_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
            lbl_size.grid(row=0, column=1, sticky="ew", padx=(5, 5), pady=2)

        # Update scrollregion when all widgets are in place
        labels_frame.update_idletasks()
        legend_canvas.config(scrollregion=legend_canvas.bbox("all"))

        # Bind mousewheel to scroll the legend_canvas
        def _on_mousewheel(event):
            legend_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_mousewheel_linux(event):
            if event.num == 4:
                legend_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                legend_canvas.yview_scroll(1, "units")

        def on_frame_configure(event):
            # Update scrollregion after resizing the labels_frame
            legend_canvas.configure(scrollregion=legend_canvas.bbox("all"))

        def on_canvas_configure(event):
            # Make sure labels_frame width fits the canvas width
            canvas_width = event.width
            legend_canvas.itemconfig(canvas_window, width=canvas_width)

        # Bind mousewheel events for both Windows and Linux
        legend_canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows
        legend_canvas.bind_all("<Button-4>", _on_mousewheel_linux)  # Linux scroll up
        legend_canvas.bind_all("<Button-5>", _on_mousewheel_linux)  # Linux scroll down
        labels_frame.bind("<Configure>", on_frame_configure)
        legend_canvas.bind("<Configure>", on_canvas_configure)

        # Dinamically change the size
        root.update_idletasks()
        width = root.winfo_reqwidth()
        height = root.winfo_reqheight()
        root.geometry(f"{width}x{height}")

        root.mainloop()

    def graphPieChartMatplotlib(self, data: pd.Series) -> None:
        valueCounts = data.value_counts().reset_index()
        valueCounts.columns = [data.name, "count"]

        # Sort by count (descending) and then by value (ascending)
        valueCounts = valueCounts.sort_values(
            by=["count", data.name], ascending=[False, True]
        )

        labels = valueCounts[data.name].values
        sizes = valueCounts["count"].values
        total = sum(sizes)

        threshold = 2

        def autopct_format(pct):
            return f"{pct:.1f}%" if pct >= threshold else ""

        finalLabels = [
            label if (size / total * 100) >= threshold else ""
            for label, size in zip(labels, sizes)
        ]

        # Get best font for CJK support
        best_font = self._get_best_font()

        colorCycle = itertools.cycle(plt.cm.tab10.colors)

        # Get the colors
        colorMap = {
            size: next(colorCycle)
            for size in sorted({int(s) for s in sizes}, reverse=True)
        }
        wedgeColors = [colorMap[int(size)] for size in sizes]

        # Plot figure
        fig, ax = plt.subplots(figsize=(6, 6))

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=finalLabels,
            autopct=autopct_format,
            startangle=0,
            shadow=False,
            textprops={"fontname": best_font},
            colors=wedgeColors,
        )

        # Calculate cumulative angles for boundaries between wedges
        cumulative = np.cumsum([0] + sizes) / total * 360

        # Draw black lines between wedges (edges)
        for i in range(len(sizes)):
            if sizes[i] != sizes[(i + 1) % len(sizes)]:
                angle = cumulative[i]  # boundary after wedge i
                theta = np.deg2rad(angle)
                r = 1
                ax.plot(
                    [0, r * np.cos(theta)],
                    [0, r * np.sin(theta)],
                    color="black",
                    linewidth=1.5,
                )

        # Add a black circular border around the pie chart
        circle = Circle((0, 0), 1, edgecolor="black", facecolor="none", linewidth=1.5)
        ax.add_patch(circle)

        ax.set_title(f"Distribution of {data.name}")
        ax.set_aspect("equal")

        # Create legend with all original labels and counts
        legendHandles = [
            plt.Rectangle((0, 0), 1, 1, facecolor=color) for color in wedgeColors
        ]

        # Calculate the maximum width needed for proper alignment
        maxLabelWidth = max(len(str(label)) for label in labels)
        maxSizeWidth = max(len(str(size)) for size in sizes)
        legendLabels = [
            f"{label:<{maxLabelWidth}} {size:>{maxSizeWidth}}"
            for label, size in zip(labels, sizes)
        ]

        legend = ax.legend(
            legendHandles,
            legendLabels,
            bbox_to_anchor=(1.02, 0, 0.07, 1),
            prop={"family": best_font},
        )

        # Adjust layout to prevent legend from being cut off
        plt.tight_layout()

        # Check if legend extends beyond figure and adjust if needed
        fig.canvas.draw()  # Ensure everything is rendered
        legend_bbox = legend.get_window_extent(fig.canvas.get_renderer())
        fig_bbox = fig.bbox

        if legend_bbox.x1 > fig_bbox.x1:
            # Legend extends beyond figure, move pie chart left
            plt.subplots_adjust(left=0.1, right=0.65)

        # pixels to scroll per mousewheel event
        d = {"down": 30, "up": -30}

        from matplotlib.transforms import Bbox

        def func(evt):
            if legend.contains(evt):
                bbox = legend.get_bbox_to_anchor()
                bbox = Bbox.from_bounds(
                    bbox.x0, bbox.y0 + d[evt.button], bbox.width, bbox.height
                )
                tr = legend.axes.transAxes.inverted()
                legend.set_bbox_to_anchor(bbox.transformed(tr))
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect("scroll_event", func)
