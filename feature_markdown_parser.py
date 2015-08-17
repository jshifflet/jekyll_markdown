
import sys
from os import walk
from os.path import splitext, join

def select_files(root, files):
    selected_files = []

    for file in files:
        #do concatenation here to get full path
        full_path = join(root, file)
        ext = splitext(file)[1]

        if ext == ".feature":
            selected_files.append(full_path)

    return selected_files

def build_recursive_dir_tree(path):
    selected_files = []

    for root, dirs, files in walk(path):
        selected_files += select_files(root, files)

    return selected_files

def read_feature_file(fd):
    in_gherkin_or_markdown = None
    output_string = ""

    for line in fd.readlines():
        #line = line.strip() + "\n"

        #if line == "\n" or line == "":
        #    continue

        if in_gherkin_or_markdown == None:
            if line.startswith("##"):
                in_gherkin_or_markdown = "markdown"
                output_string += line.replace("##", "")
            else:
                in_gherkin_or_markdown = "gherkin"
                output_string += "{% highlight cucumber %}\n"
                output_string += line

        elif in_gherkin_or_markdown == "markdown":
            if line.startswith("##"):
                output_string += line.replace("##", "")
            else:
                in_gherkin_or_markdown = "gherkin"
                output_string += "{% highlight cucumber %}\n"
                output_string += line
        elif in_gherkin_or_markdown == "gherkin":
            if line.startswith("##"):
                output_string += "{% endhighlight %}\n"
                output_string += line.replace("##", "")
                in_gherkin_or_markdown = "markdown"
            else:
                output_string += line

    if in_gherkin_or_markdown == "gherkin":
        output_string += "{% endhighlight %}\n"

    return output_string

def generate_front_matter(file):
    return "---\nlayout: post\ntitle: " + file.split("/")[-1].replace(".feature", "")+ "\n---\n\n"

rootdir = sys.argv[1]
base_name = sys.argv[2]

files = build_recursive_dir_tree(rootdir)

for file in files:
    fd = open(file, "r")

    output_string = generate_front_matter(file)

    output_string += read_feature_file(fd)
    fd.close()

    fd_out = open(base_name + "-" + file.split("/")[-1].replace(".feature", "") + ".markdown", "w")
    fd_out.write(output_string)
    fd_out.close()
