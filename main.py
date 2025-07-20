import miiPlaza

if __name__ == "__main__":

    # We open the file
    with open("meet.dat", "rb") as f:
        data = f.read()

    plaza = miiPlaza.MiiPlaza(data)

    with open("miis.csv", "w") as f:
        # We write the Mii data to a CSV file
        plaza.getMiiData().to_csv(f, index=False)

    with open("miisUnknown.csv", "w") as f:
        plaza.getMiiUnknownBytes().to_csv(f, index=False)
