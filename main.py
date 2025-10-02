import sys 
from scripts.runtime import main_loop
Errors = {
    "1001": "No Database Selected",
    "1002": "More Than One Argument Passed"
}

def main():
    if len(sys.argv) < 2:
        print(f"{Errors["1001"]}")
    elif len(sys.argv) > 2:
        print(f"{Errors["1002"]}")
    else:
        variable = sys.argv[1]
        print(f"Database Selected: {variable}")

        main_loop(variable) # main loop


main()        