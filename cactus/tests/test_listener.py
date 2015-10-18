import os
import tempfile
import threading
import unittest2 as unittest

from cactus.listener import PollingListener
from cactus.tests.compat import has_symlink

try:
    from cactus.listener import FSEventsListener
except ImportError:
    FSEventsListener = None


def sleep(s):
    # time.sleep(s)
    event = threading.Event()
    event.wait(timeout=s)


class PollingListenerTest(unittest.TestCase):

    def setUp(self):
        self._callbacks = []
        self._callback_count = 0
        self.lock = threading.Lock()


    def _callback(self, event):
        with self.lock:
            self._callbacks.append(event)

    @property
    def callbacks(self):
        with self.lock:
            return self._callbacks

    def wait(self):

        time_total = 0
        time_increment = 0.03
        time_max = 3.0

        while True:

            # print time_total

            self.assertEqual(time_total < time_max, True, "Timeout")

            if len(self.callbacks) == self._callback_count + 1:
                self._callback_count += 1
                return

            sleep(time_increment)
            time_total += time_increment

    def create_listener(self, path):
        return PollingListener(path, self._callback)

    @unittest.skipUnless(has_symlink, "No symlink support")
    def testSymlinkFolder(self):

        path1 = os.path.realpath(os.path.join(tempfile.mkdtemp(), "watched"))
        path2 = os.path.realpath(os.path.join(tempfile.mkdtemp(), "linked"))

        os.mkdir(path1)
        os.mkdir(path2)

        path_link = os.path.join(path1, "path2")
        path_link_file = os.path.join(path2, "file.js")
        path_link_file_original = os.path.join(path_link, "file.js")

        os.symlink(path2, path_link)

        with open(path_link_file, "w") as f:
            f.write("hello1")

        self.listener = self.create_listener(path1)
        self.listener.run()

        sleep(1)

        with open(path_link_file, "w") as f:
            f.write("hello2")

        self.wait()

        self.assertEqual(len(self.callbacks), 1)
        self.assertEqual(self.callbacks[0]["changed"], [path_link_file_original])

    def testSimpleFile(self):

        path_watch = os.path.realpath(os.path.join(tempfile.mkdtemp(), "watched"))
        path_file = os.path.join(path_watch, "file.js")

        os.mkdir(path_watch)

        self.listener = self.create_listener(path_watch)
        self.listener.run()

        sleep(1)

        with open(path_file, "w") as f:
            f.write("hello1")

        self.wait()

        self.assertEqual(len(self.callbacks), 1)
        self.assertEqual(self.callbacks[0]["added"], [path_file])

        os.remove(path_file)

        self.wait()

        self.assertEqual(len(self.callbacks), 2)
        self.assertEqual(self.callbacks[1]["deleted"], [path_file])

    @unittest.skipUnless(has_symlink, "No symlink support")
    def testSymlinkFile(self):

        path_watch = os.path.realpath(os.path.join(tempfile.mkdtemp(), "watched"))
        path_linked = os.path.realpath(os.path.join(tempfile.mkdtemp(), "linked"))

        os.mkdir(path_watch)
        os.mkdir(path_linked)

        file_actual1 = os.path.join(path_linked, "framer.js")
        file_actual2 = os.path.join(path_linked, "framer.js")
        file_link = os.path.join(path_watch, "framer.js")

        with open(file_actual1, "w") as f:
            f.write("hello1")

        with open(file_actual2, "w") as f:
            f.write("hello2")

        os.symlink(file_actual1, file_link)

        self.listener = self.create_listener(path_watch)
        self.listener.run()

        if hasattr(self.listener, "streamed_folders"):
            self.assertEqual(len(self.listener.streamed_folders), 2)

        sleep(1)

        # Change the linked file
        with open(file_actual1, "w") as f:
            f.write("hello1")

        self.wait()

        self.assertEqual(len(self.callbacks), 1)
        self.assertEqual(self.callbacks[0]["changed"], [file_link])

        # sleep(1)

        # Now change a file in the same dir as the link, this should not do anything
        with open(file_actual2, "w") as f:
            f.write("hello333")

        sleep(1)

        with open(file_actual1, "w") as f:
            f.write("hello3223")

        self.wait()

        self.assertEqual(len(self.callbacks), 2)
        self.assertEqual(self.callbacks[0]["changed"], [file_link])

if FSEventsListener:

    class FSEventsListenerTest(PollingListener):

        def create_listener(self, path):
            return FSEventsListener(path, self._callback)
