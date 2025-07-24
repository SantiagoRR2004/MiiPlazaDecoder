import pandas as pd
import mii
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import Scrollbar, Canvas
from matplotlib.patches import Circle
import tkinter.font as tkfont
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

        # Plot figure
        fig, ax = plt.subplots(figsize=(6, 6))

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=final_labels,
            autopct=autopct_format,
            startangle=0,
            shadow=False,
            textprops={"fontname": "SimSun"},
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

        temp_frame = tk.Frame(hidden_win)
        temp_frame.pack()

        # Create labels in temp_frame
        test_font = tkfont.Font(family="SimHei", size=9)

        for idx, (label, size) in enumerate(zip(labels, sizes)):
            lbl_label = tk.Label(temp_frame, text=label, font=test_font, anchor="w")
            lbl_size = tk.Label(temp_frame, text=str(size), font=test_font, anchor="e")
            lbl_label.grid(row=idx, column=0, sticky="w", padx=5, pady=2)
            lbl_size.grid(row=idx, column=1, sticky="e", padx=5, pady=2)

        temp_frame.update_idletasks()
        needed_width = temp_frame.winfo_reqwidth()

        # Clean up
        hidden_win.destroy()

        # Matplotlib canvas
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Frame for scrollbar and legend text
        frame = tk.Frame(root)
        frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a scrollbar and a canvas to hold the legend labels
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        legend_canvas = tk.Canvas(
            frame, width=needed_width, height=400, yscrollcommand=scrollbar.set
        )
        legend_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        scrollbar.config(command=legend_canvas.yview)

        # Create a frame inside the canvas to hold labels
        labels_frame = tk.Frame(legend_canvas)
        legend_canvas.create_window((0, 0), window=labels_frame, anchor="nw")

        # Add legend entries as labels inside labels_frame
        for idx, (label, size) in enumerate(zip(labels, sizes)):
            lbl_label = tk.Label(
                labels_frame, text=label, font=("SimSun", 9), anchor="w"
            )
            lbl_size = tk.Label(
                labels_frame, text=str(size), font=("SimSun", 9), anchor="e"
            )
            lbl_label.grid(row=idx, column=0, sticky="w", padx=5, pady=2)
            lbl_size.grid(row=idx, column=1, sticky="ew", padx=5, pady=2)

        # Update scrollregion when all widgets are in place
        labels_frame.update_idletasks()
        legend_canvas.config(scrollregion=legend_canvas.bbox("all"))

        # Bind mousewheel to scroll the legend_canvas
        def _on_mousewheel(event):
            legend_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        legend_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Dinamically change the size
        root.update_idletasks()
        width = root.winfo_reqwidth()
        height = root.winfo_reqheight()
        root.geometry(f"{width}x{height}")

        root.mainloop()
