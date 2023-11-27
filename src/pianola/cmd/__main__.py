from pianola.cmd import main

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        exit("error: " + str(e))
