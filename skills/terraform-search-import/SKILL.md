---
name: terraform-search-import
description: Adopt existing infrastructure into OpenTofu or Terraform state. Use when importing unmanaged resources, reconciling state with real infrastructure, auditing what already exists, or migrating manually created resources into IaC. In OpenTofu environments, prefer manual discovery plus import blocks or tofu import; do not default to Terraform Search or terraform query unless the user explicitly works in Terraform and that feature is available.
metadata:
  version: "2.0"
---

# OpenTofu-Oriented Import Guide

This repository is OpenTofu-first. That changes the default import workflow.

OpenTofu supports import blocks and the `tofu import` command, but Terraform Search and `terraform query` are Terraform-specific features and should not be the default path here.

## Default decision rule

1. Identify the runtime.
2. If the repo uses OpenTofu, use manual discovery plus import blocks or `tofu import`.
3. Only consider Terraform Search if the user explicitly says they are using Terraform with that feature available.

In this repository, assume step 2 unless the user says otherwise.

## OpenTofu workflow

### 1. Discover existing resource IDs outside OpenTofu

Use the provider's CLI, console, or API to discover the existing objects and their import IDs.

Examples:

- OCI CLI for OCI resources
- AWS CLI for AWS resources
- cloud console lookups when no reliable CLI exists

### 2. Write the target resource blocks first

Create the resource or module address where the object should live long-term.

- Import into the final module path, `for_each` key, or `count` index.
- Do not import into a temporary address unless you also plan the follow-up state move.

```hcl
resource "aws_instance" "web" {
  # Fill in the intended managed configuration.
}
```

### 3. Prefer config-driven import blocks for tracked changes

Use `import` blocks when the import should be visible in version control and reviewed with the rest of the configuration.

```hcl
import {
  to = aws_instance.web
  id = "i-1234567890abcdef0"
}

resource "aws_instance" "web" {
  # Fill in the intended managed configuration.
}
```

### 4. Plan and apply from the OpenTofu root

In this repo:

```bash
cd terraform
tofu init
tofu plan -var-file=terraform.tfvars
tofu apply -var-file=terraform.tfvars
```

For a focused import review, a plain `tofu plan` is also acceptable when no tfvars are needed.

### 5. Clean up imported configuration

After import:

- remove computed-only attributes
- replace copied literals with variables or locals where appropriate
- preserve the repository's naming and module structure
- keep only the arguments required to express intent and avoid drift

## When to use `tofu import`

Use the CLI command when you need a one-off state attachment and do not want to keep an import block in the codebase.

```bash
tofu import aws_instance.web i-1234567890abcdef0
tofu import 'aws_iam_user.users["alice"]' alice
tofu import module.network.aws_vpc.main vpc-12345678
```

Prefer import blocks instead when the import is part of a code reviewable migration.

## Multiple resources

For many similar resources:

- generate import blocks or import commands with a small script
- sanitize names into stable HCL labels
- review the generated addresses before applying

If you need a repeatable template for manual discovery, read [references/MANUAL-IMPORT.md](/Users/eder/Code/im/infra/.claude/skills/terraform-search-import/references/MANUAL-IMPORT.md).

## Resource-address rules

- Each remote object must map to exactly one OpenTofu resource address.
- Never import the same object to multiple addresses.
- For `for_each`, import directly into the keyed address.
- For `count`, import directly into the indexed address.
- For modules, use the fully qualified module address.

## Repository-specific guidance

When adopting resources into this repo:

- run from `terraform/`
- keep OCI compartment OCIDs centralized instead of scattering them into many resources
- preserve the repo's `servers`, `server_defaults`, and compartment-alias model
- import into the real module structure rather than flattening resources into the root

## Terraform-only path

If the user explicitly wants Terraform Search or `terraform query`, stop and confirm the runtime first.

Only use that path when all of the following are true:

- the runtime is Terraform, not OpenTofu
- the installed Terraform version supports the feature needed
- the provider supports the discovery capability involved

Otherwise, fall back to the manual OpenTofu workflow.

## What to avoid

- Do not default to `terraform query` in an OpenTofu repo.
- Do not paste provider-generated full resource state into version-controlled HCL without cleanup.
- Do not import into placeholder addresses you do not intend to keep.
- Do not run import operations from the repository root in this repo.

## Completion Checklist

Before finishing an import/adoption task in this repository:

1. Verify the final resource address is correct.
2. Run `tofu fmt -recursive` from `terraform/` if HCL changed.
3. Run `tofu validate`.
4. Run `tofu plan` or `tofu plan -var-file=terraform.tfvars` to confirm the imported object matches the intended configuration.
