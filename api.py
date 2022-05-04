import Levenshtein


def isSomething(inp, list_of_interested):
    ratio = Levenshtein.ratio(inp, list_of_interested)
    # print(f"{inp} == {list_of_interested} ? Accuracy: {ratio}")

    if ratio > 0.77:
        return True
    else:
        return False


if __name__ == "__main__":
    with open("keywords\\animes.txt", "r") as f:
        animes = f.read().splitlines()
    with open("keywords\\characters.txt", "r") as f:
        characters = f.read().splitlines()
    ok = "Bakery Girl"
    for i in characters:
        ratio = Levenshtein.ratio(ok, i)
        print(f"Accuracy: {ratio} - {i}")
