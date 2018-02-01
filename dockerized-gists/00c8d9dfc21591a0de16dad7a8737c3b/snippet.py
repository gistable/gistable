from IPython.core.magic import Magics, magics_class, line_magic


@magics_class
class Imports(Magics):

    @line_magic
    def imports(self, opts):

        lines = []

        if "os" in opts:
            lines.extend([
                "import os",
                "import os.path as op",
            ])

        lines.extend([
            "import numpy as np",
            "import pandas as pd",
            "import seaborn as sns",
            "import matplotlib.pyplot as plt",
        ])

        if "fmri" in opts:
            lines.extend([
                "import nibabel as nib",
                "import lyman",
            ])

        self.shell.set_next_input("\n".join(lines), replace=True)


ip = get_ipython()
ip.register_magics(Imports)
