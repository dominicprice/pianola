from pianola.cmd import main, parse_args

if __name__ == "__main__":
    args = parse_args()
    try:
        main(args)
    except Exception as e:
        exit("error: " + str(e))
