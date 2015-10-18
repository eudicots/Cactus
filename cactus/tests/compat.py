import os
import os.path
import shutil
import tempfile


has_symlink = False


compat_test_dir = tempfile.mkdtemp()

# Check for symlink support (available and usable)

src = os.path.join(compat_test_dir, "src")
dst = os.path.join(compat_test_dir, "dst")

with open(src, "w"):
    pass

try:
    os.symlink(src, dst)
except (AttributeError, OSError):
    # AttributeError if symlink is not available (Python <= 3.2 on Windows)
    # OSError if we don't have the symlink privilege (on Windows)
    pass  # Leave has_symlink false
else:
    has_symlink = True


shutil.rmtree(compat_test_dir)
