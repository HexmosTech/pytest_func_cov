import pytest
import os


module_init = """
# AAliased should not be indexed as it is not defined in __init__

from .module1 import A as AAliased
"""

module1 = """
from mypackage.module2 import f

def c():
    f()
    pass
"""


module2 = """
def f():
    pass

def g():
    pass
    
def h():
    g()
    pass    
"""
test_module1_0 = """
from mypackage.module1 import c
from mypackage.module2 import h
def test_c():
    c()

def test_h():
    h()
"""

test_module1_1 = """
# However calls on AAliased should be indexed
from mypackage import AAliased
from mypackage.module1 import A

def test_aaliased_d():
    AAliased.d()

def test_alias_is_identical():
    assert AAliased is A

"""


@pytest.fixture
def base_package(testdir):

    test_dir = testdir.mkdir("tests")
    project_dir = testdir.mkpydir("mypackage")


    with project_dir.join("module2.py").open("w") as f:
        f.write(module2)

    with project_dir.join("module1.py").open("w") as f:
        f.write(module1)

    with test_dir.join("test_module.py").open("w") as f:
        f.write(test_module1_0)

    yield testdir


@pytest.fixture
def package_with_alias(base_package):
    path_to_init = base_package.tmpdir.join("mypackage", "__init__.py")
    path_to_test = base_package.tmpdir.join("tests", "test_module_2.py")

    with open(path_to_init, "w") as f:
        f.write(module_init)

    with open(path_to_test, "w") as f:
        f.write(test_module1_1)

    yield base_package

    os.remove(path_to_init)
    os.remove(path_to_test)


def test_base_package(base_package):
    res = base_package.runpytest("--func_cov=mypackage", "tests/")
    lines = ("mypackage/module1.py +4 +1 +75%", "TOTAL +4 +1 +75%")

    res.stdout.re_match_lines(lines)


def test_base_package_with_missing(base_package):
    res = base_package.runpytest(
        "--func_cov=mypackage", "--func_cov_report=term-missing", "tests/"
    )
    lines = (
        "mypackage/module1.py +7 +5 +28% +<lambda>, A.a, A.b, A.d, A.c",
        "TOTAL +7 +5 +28%",
    )

    res.stdout.re_match_lines(lines)


def test_package_with_alias(package_with_alias):
    res = package_with_alias.runpytest(
        f"--func_cov=mypackage", "tests/test_module_2.py"
    )
    lines = ("mypackage/module1.py +7 +6 +14%", "TOTAL +7 +6 +14%")

    res.stdout.re_match_lines(lines)


def test_package_with_alias_and_missing(package_with_alias):
    res = package_with_alias.runpytest(
        "--func_cov=mypackage",
        "--func_cov_report=term-missing",
        "tests/test_module_2.py",
    )
    lines = (
        "mypackage/module1.py +7 +6 +14% +<lambda>, A.__getitem__, A.__init__, A.a, A.b, A.c",
        "TOTAL +7 +6 +14%",
    )

    res.stdout.re_match_lines(lines)
