from typing import Any

from devtool.software_list import GoPackage


def renovate_json(go_packages: list[GoPackage]) -> dict[str, Any]:
    return {
        "$schema": "https://docs.renovatebot.com/renovate-schema.json",
        "extends": ["config:recommended"],
        "packageRules": [
            {
                "matchManagers": ["gomod"],
                "enabled": False,
            },
            {
                # Don't update any Go dependencies unless they're the direct dependencies
                # that we care about. Updating indirect dependencies could cause unexpected
                # behavior when the upstream tool builds with an older version of a library
                # and we build with a newer version.
                "matchManagers": ["gomod"],
                "matchPackageNames": [p.module_path for p in go_packages],
                "enabled": True,
                "groupName": "Go dependencies",
            },
        ],
        # And run `go mod tidy` afterwards to update the dependencies of our direct
        #  dependencies **when necessary** (according to Go's Minimal Version Selection).
        "postUpdateOptions": ["gomodTidy"],
    }
