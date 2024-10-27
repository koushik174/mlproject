from typing import List
from setuptools import find_packages,setup
HYPEN_DOT_E='e .'
def get_requirments(file_path:str)-> List[str]:
    '''
    this function will call the list of requirements
    '''
    requirments=[]
    with open(file_path) as file_obj:
        requirments=file_obj.readlines()
        requirments=[req.replace("\n","")for req in requirments]
    if HYPEN_DOT_E in requirments:
        requirments.remove(HYPEN_DOT_E)
setup(
name='mlproject',
version='0.0.1',
author='koushik174',
author_email='kancharlakoushik8547@gmail.com',
packages=find_packages(),
install_requires=get_requirments('requirments.txt')
)