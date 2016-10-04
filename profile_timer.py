import unittest
import time


class Timer(object):
    """Simple profiling timer allowing elapsed time to me measured
       for multiple execution spans, tagged appropriately.
    """

    def __init__(self):
        self.times = {}

    def reset(self, tag):
        self.times[tag] = [-1, -1]

    def start(self, tag, reset=False):
        if reset or tag not in self.times:
            self.times[tag] = [-1, 0.0]
        self.times[tag][0] = time.time()

    def stop(self, tag):
        stime = time.time()
        if self.times[tag][0] <= 0:
            raise RuntimeError('stop() called for a stopped tag')
        self.times[tag][1] += stime - self.times[tag][0]
        self.times[tag][0] = -1

    def elapsed(self, tag):
        return self.times[tag][1]

    def show_all(self):
        all_elapsed = [(tag, self.times[tag][1]) for tag in self.times.iterkeys()]
        list_of_tuples = sorted(all_elapsed, key=lambda tpl: tpl[1], reverse=True)
        return "\n".join(["%-12s: %.4f" % (key, value) for key, value in list_of_tuples])


class TestTimer(unittest.TestCase):

    def test_creation(self):
        timer = Timer()
        self.assertEqual({}, timer.times)

    def test_reset(self):
        timer = Timer()
        tag = 'testreset'
        timer.reset(tag)
        self.assertEqual([-1, -1], timer.times[tag])

    def test_start(self):
        timer = Timer()
        t = time.time()
        tag = 'teststart'
        timer.start(tag)
        self.assertTrue(tag in timer.times)
        self.assertAlmostEqual(t, timer.times[tag][0], places=3)

    def test_stop(self):
        timer = Timer()
        tag = 'teststop'
        timer.start(tag)
        time.sleep(0.14)
        timer.stop(tag)
        self.assertEqual(timer.times[tag][0], -1)
        self.assertAlmostEqual(timer.times[tag][1], 0.14, places=2)
        self.assertRaises(RuntimeError, timer.stop, tag)

    def test_start_reset(self):
        timer = Timer()
        tag = 'teststartreset'
        timer.start(tag)
        time.sleep(0.07)
        timer.stop(tag)
        timer.start(tag, reset=False)
        time.sleep(0.04)
        timer.stop(tag)
        timer.start(tag, reset=True)
        time.sleep(0.05)
        timer.stop(tag)

    def test_elapsed(self):
        timer = Timer()
        tag = 'testelapsed'
        timer.start(tag)
        time.sleep(0.13)
        timer.stop(tag)

    def test_standard_scenario(self):
        timer = Timer()
        timer.start('all')
        timer.start('tag1')
        time.sleep(0.16)
        timer.stop('tag1')
        time.sleep(0.12)
        timer.start('tag1')
        time.sleep(0.19)
        timer.stop('tag1')
        timer.stop('all')
        print(timer.times)
        timer.reset('tag1')
        elapsed = timer.elapsed('tag1')
        self.assertEqual(-1, elapsed)

    def test_show_all(self):
        timer = Timer()
        timer.start('tag1')
        time.sleep(0.1)
        timer.start('tag2')
        time.sleep(0.1)
        timer.stop('tag2')
        time.sleep(0.1)
        timer.stop('tag1')
        print(timer.show_all())


if __name__ == '__main__':
    unittest.main()
