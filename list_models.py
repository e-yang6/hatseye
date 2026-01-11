#!/usr/bin/env python3
"""
List available Roboflow projects and models
"""

from roboflow import Roboflow

API_KEY = "dyQPAMFEMQE8DzcdptsU"

try:
    rf = Roboflow(api_key=API_KEY)
    workspace = rf.workspace()

    print(f"Workspace: {workspace.name}")
    print(f"URL: {workspace.url}")
    print("\nProjects:")

    for project in workspace.projects():
        print(f"\n  Project: {project.name}")
        print(f"  ID: {project.id}")
        print(f"  Type: {project.type}")

        try:
            versions = project.versions()
            print(f"  Versions: {len(versions)}")
            for version in versions:
                print(f"    - Version {version.version}: {project.id}/{version.version}")
        except Exception as e:
            print(f"    Could not list versions: {e}")

except Exception as e:
    print(f"Error: {e}")
    print("\nTry checking your API key and internet connection")
