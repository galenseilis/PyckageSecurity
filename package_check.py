import subprocess
import requests
import yaml

with open('packages.yaml', 'r') as f:
    packages = yaml.safe_load(f)['packages']

package_versions = {}
for package in packages:
    response = requests.get(f'https://pypi.org/pypi/{package}/json')
    if response.ok:
        data = response.json()
        versions = list(data['releases'].keys())
        package_versions[package] = versions

security_reports = {}
for package, versions in package_versions.items():
    for version in versions:
        try:
            command = f'bandit -r --format yaml {package}=={version}'
            result = subprocess.check_output(command, shell=True)
            issues = yaml.safe_load(result)
            security_reports.setdefault(package, {}).setdefault(version, {}).update({'issues': issues})
        except subprocess.CalledProcessError as e:
            print(f'Error getting report for {package}=={version}: {e}')

with open('security_reports.yaml', 'w') as f:
    yaml.safe_dump(security_reports, f)

