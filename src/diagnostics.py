import importlib
import sys


def get_env_diagnostics():
    info = {
        'python_version': sys.version,
        'python_executable': sys.executable,
    }

    for pkg in ['pandas', 'numpy', 'openpyxl', 'streamlit']:
        try:
            mod = importlib.import_module(pkg)
            info[f'{pkg}_version'] = getattr(mod, '__version__', 'unknown')
        except Exception as e:
            info[f'{pkg}_version'] = f'NOT AVAILABLE ({type(e).__name__}: {e})'

    return info
