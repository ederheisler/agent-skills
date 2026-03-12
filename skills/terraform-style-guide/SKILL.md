---
name: terraform-style-guide
description: Write and review OpenTofu-first HCL using current style conventions and safe infrastructure patterns. Use whenever editing Terraform or OpenTofu configuration, modules, variables, outputs, providers, or imports. Prefer OpenTofu commands and OpenTofu documentation unless the user explicitly needs Terraform-only behavior.
metadata:
  version: "2.0"
---

# OpenTofu Style Guide

Write HCL that is correct, readable, and OpenTofu-first.

In this repository, OpenTofu is the default runtime. Command examples, validation steps, and workflow choices should therefore use `tofu`, not `terraform`, unless the user explicitly asks for Terraform.

## Runtime Defaults

- Run infrastructure commands from `terraform/`, not from the repository root.
- Prefer these commands for verification:

```bash
cd terraform
tofu fmt -recursive
tofu validate
tofu plan -var-file=terraform.tfvars
```

- Treat OpenTofu documentation as the primary reference for language and CLI behavior.
- Keep HCL broadly Terraform-compatible unless the task specifically benefits from an OpenTofu-only feature.

## Repository Layout

Follow the repository's existing file structure instead of imposing a generic layout.

For this repo, the expected root layout is:

- `providers.tf` for `terraform {}` version/provider requirements and provider configuration
- `main.tf` for root wiring and normalization
- `variables.tf` for input schema and validation
- `outputs.tf` for exported values
- modules under `terraform/modules/*`

If a file already exists for a concern, extend that file instead of creating a parallel convention.

## Style Rules

### Formatting

- Use two spaces per nesting level.
- Let `tofu fmt` define the final formatting.
- Keep consecutive single-line assignments aligned when `tofu fmt` preserves alignment.

```hcl
resource "oci_core_instance" "api" {
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_id
  display_name        = var.display_name
  shape               = var.shape
}
```

### Block Ordering

- Put meta-arguments first.
- Put regular arguments next.
- Put nested blocks after arguments, separated by a blank line when that improves readability.
- Put lifecycle and other meta-argument blocks last.

```hcl
resource "oci_core_instance" "api" {
  for_each = var.instances

  availability_domain = each.value.availability_domain
  compartment_id      = each.value.compartment_id
  display_name        = each.value.display_name
  shape               = each.value.shape

  source_details {
    source_type = "image"
    source_id   = each.value.image_id
  }

  lifecycle {
    create_before_destroy = true
  }
}
```

### Naming

- Use lowercase with underscores for variables, locals, outputs, and resource labels.
- Use descriptive singular labels.
- Avoid redundant labels like `instance_instance` or `server_resource`.
- Use stable, intention-revealing names such as `network`, `server`, `public_ip`, `shape_profiles`, or `normalized_servers`.

## Modeling Guidance

### Prefer explicit data flow

- Normalize user input in `locals` before feeding modules.
- Pass resolved values into modules instead of repeating fallback logic in many places.
- Keep raw provider IDs centralized when the repo already follows that pattern.

In this repo specifically:

- `project_name` is a global name prefix.
- `servers` is the map of real server definitions.
- `server_defaults` holds values shared by most servers.
- `compartments` and `compartment_ocids` should centralize compartment selection instead of scattering raw OCIDs across resources.

### Prefer `for_each` over `count`

Use `for_each` when instances have meaningful keys or when stable addressing matters.

```hcl
module "server" {
  for_each = local.normalized_servers

  source = "./modules/server"

  project_name           = var.project_name
  server_name            = each.key
  compute_compartment_id = each.value.compartment_ocid
}
```

Use `count` mainly for simple on/off creation where identity is unimportant.

### Variables and outputs

- Every variable should have a clear `description` and explicit `type`.
- Add validation when a bad value would otherwise fail late or obscurely.
- Every output should have a `description`.
- Mark sensitive data as `sensitive = true`.

```hcl
variable "shape_profile" {
  description = "Logical shape profile name resolved through shape_profiles."
  type        = string

  validation {
    condition     = contains(keys(var.shape_profiles), var.shape_profile)
    error_message = "shape_profile must reference a key in shape_profiles."
  }
}
```

## Security and Safety

- Never hardcode credentials, private keys, tokens, or tenancy secrets.
- Prefer variables for sensitive inputs and mark them sensitive when appropriate.
- Avoid unnecessary public exposure in generated infrastructure.
- Keep imports, state moves, and destructive changes explicit in plans.

## Imports and Existing Infrastructure

When adopting existing resources:

- Write the target resource block at its final address first.
- Prefer config-driven `import` blocks when the workflow is going into version control.
- Use `tofu import` only when a one-off state attachment is more practical than keeping import blocks in code.

## What to avoid

- Do not introduce Terraform-only CLI guidance into this repo unless the user asks for it.
- Do not create new top-level conventions that fight the existing repository structure.
- Do not duplicate fallback logic across modules when a single normalized local can own it.
- Do not leave generated or imported configuration full of computed-only attributes.

## Completion Checklist

Before finishing a change to OpenTofu code in this repository:

1. Run `tofu fmt -recursive` from `terraform/`.
2. Run `tofu validate` from `terraform/`.
3. If inputs or resource wiring changed materially, run `tofu plan -var-file=terraform.tfvars` when local credentials and tfvars are available.
