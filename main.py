import miiPlaza

if __name__ == "__main__":
    
    # We open the file
    with open("meet.dat", "rb") as f:
        data = f.read()

    plaza = miiPlaza.MiiPlaza(data)
