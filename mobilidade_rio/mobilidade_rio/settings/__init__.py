"""
Settings module - v1.1 - 2022/10/25

You need to set an environment variable in your shell
Default is 'dev'.

Bash:
export site1="dev"

Powershell:
$env:site1="dev"

Command Prompt:
set site1=dev
"""

from warnings import warn
from .base import *
import os
from .utils import _yellow, _reset

project_name = "mobilidade_rio"

# if none, warn and use dev
if os.getenv(project_name) is None:
   warn(
f"""{_yellow}
Enviroment variable '{project_name}' is not defined, by default 'dev' settings wil be used.

How to set enviroment variables:
bash: export {project_name}="prod"
PS:   $env:{project_name}="prod"
CMD:  set {project_name}=prod
{_reset}"""
   )
   from .dev import *

# prod
elif os.environ[project_name] == 'prod':
   from .prod import *

# if any other, use dev
else:
   from .dev import *
