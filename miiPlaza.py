import pandas as pd
import mii
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import tkinter as tk
from matplotlib.patches import Circle
import tkinter.font as tkfont
import itertools
import numpy as np
import sys


class MiiPlaza:
    """
    There are more things that could be added here like
    the puzzle pieces from:

    https://www.reddit.com/r/3dshacks/comments/4c5rcp/streetpass_mii_plaza_puzzle_swap_unlock_all/
    """

    MII_PLAZA_SIZE = 393216

    def __init__(self, bytesData: bytes) -> None:
        """
        Initialize MiiPlaza object with bytes data

        Args:
            - bytesData (bytes): The raw bytes data of the Mii

        Returns:
            - None
        """
        assert len(bytesData) == self.MII_PLAZA_SIZE, "Invalid Mii Plaza size"
        self.bytesData = bytesData
        self.setMiis()

    def setMiis(self) -> None:
        """
        Set all Mii attributes by decoding the bytes data
        They are stored beginning on the 14154 byte.

        Args:
            - None

        Returns:
            - None
        """
        miis = []
        pos = 14154

        while self.bytesData[pos] != 0:
            miiData = self.bytesData[pos : pos + mii.Mii.MII_SIZE]
            miis.append(mii.Mii(miiData))
            pos += mii.Mii.MII_SIZE

        self.miis = miis

    def getMiiData(self) -> pd.DataFrame:
        """
        Get Mii data as a pandas DataFrame

        Args:
            - None

        Returns:
            - pd.DataFrame: DataFrame containing Mii names and creators
        """
        data = [mii.getData() for mii in self.miis]
        return pd.DataFrame(data)

    def getMiiUnknownBytes(self) -> pd.DataFrame:
        """
        Get Mii unknown bytes as a pandas DataFrame

        Args:
            - None

        Returns:
            - pd.DataFrame: DataFrame containing Mii names and unknown bytes
        """
        data = [mii.getUnkownBytes() for mii in self.miis]
        return pd.DataFrame(data)

    def getMiiUnknownBits(self) -> pd.DataFrame:
        """
        Get Mii unknown bits as a pandas DataFrame

        Args:
            - None

        Returns:
            - pd.DataFrame: DataFrame containing Mii names and unknown bits
        """
        data = [mii.getUnknownBits() for mii in self.miis]
        return pd.DataFrame(data)

    def findPossibleBits(self, classifier: pd.DataFrame, nBits: int) -> list:
        """
        This is to help find where possible characteristics are
        stored in the Mii data.

        The classifier should have a column named 'Name',
        another column named 'Creator',
        and the final one to have the value of the characteristic.

        We will find all the nBits bits that are together that
        have different values for each of the values of the characteristic.

        Args:
            - classifier (pd.DataFrame): DataFrame containing classifier data
            - nBits (int): Number of bits to find

        Returns:
            - list: List of possible bits
        """
        unknownBits = self.getMiiUnknownBits()
        classifierName = [
            col for col in classifier.columns if col not in ("Name", "Creator")
        ][0]

        # Normalize "Creator" in both dataframes
        classifier["Creator"] = classifier["Creator"].fillna("")
        unknownBits["Creator"] = unknownBits["Creator"].fillna("")

        combinedDf = classifier.merge(unknownBits, on=["Name", "Creator"], how="inner")
        combinedDf = combinedDf.drop(columns=["Name", "Creator"])

        groupedDf = combinedDf.groupby(classifierName)
        bitColumns = [col for col in combinedDf.columns if col != classifierName]

        possibleBits = []

        for i in range(len(bitColumns) - nBits + 1):
            group = bitColumns[i : i + nBits]

            # Check that the group is ascending and only 1 distance between bits
            if max(group) - min(group) == nBits - 1:

                valid = True

                for cl, group_df in groupedDf:
                    groupBits = group_df[group]

                    # Check that all Miis in cl have the same value
                    # We find the opposite
                    if (groupBits.nunique() != 1).any():
                        valid = False
                        break

                if valid:

                    # Now we check that all groups have different values
                    patterns = (
                        groupedDf[group].first().apply(lambda row: tuple(row), axis=1)
                    )
                    if patterns.is_unique:
                        possibleBits.append(group)

        return possibleBits

    def hexdump(self, width=16) -> str:
        """
        Get a hex dump of the Mii Plaza data

        Args:
            - None

        Returns:
            - str: Hex dump of the Mii Plaza data
        """
        toret = ""
        for offset in range(0, len(self.bytesData), width):
            chunk = self.bytesData[offset : offset + width]
            hex_bytes = " ".join(f"{b:02X}" for b in chunk)
            ascii_bytes = "".join((chr(b) if 32 <= b < 127 else ".") for b in chunk)

            # Padding for shorter lines
            hex_bytes = hex_bytes.ljust(width * 3)

            line = f"{hex_bytes}\t{ascii_bytes}"
            toret += line + "\n"

        return toret

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

    def graphPieChart(self, column: str) -> None:
        miiDf = self.getMiiData()

        valueCounts = miiDf[column].value_counts().reset_index()
        valueCounts.columns = [column, "count"]

        # Sort by count (descending) and then by value (ascending)
        valueCounts = valueCounts.sort_values(
            by=["count", column], ascending=[False, True]
        )

        labels = valueCounts[column].values
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

        ax.set_title(f"Distribution of {column}")
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
