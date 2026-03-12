---
name: terraform-test
description: Write and review OpenTofu tests using .tftest.hcl files and the tofu test command. Use when creating module tests, validating plan or apply behavior, checking outputs and validations, or troubleshooting OpenTofu test syntax and execution. In this repository, prefer OpenTofu commands and be cautious with apply-based tests against live OCI resources.
metadata:
  version: "2.0"
---

# OpenTofu Test Guide

Use OpenTofu's built-in test framework to verify module behavior without relying on ad hoc shell scripts.

In this repository, test guidance should be OpenTofu-first. Use `tofu test`, not `terraform test`, unless the user explicitly asks for Terraform.

## Defaults

- Put test files in a `tests/` directory when the module or root config is large enough to justify it.
- Use `.tftest.hcl` files.
- Prefer plan-mode tests for fast, low-risk validation.
- Use apply-mode tests only when you must verify real provider behavior.
- In this repo, run tests from `terraform/`.

## Test execution

```bash
cd terraform
tofu test
tofu test -test-directory=tests
tofu test -filter=tests/main.tftest.hcl
tofu test -verbose
tofu test -json
```

If module structure or providers changed, run `tofu init` before `tofu test`.

## Basic structure

OpenTofu tests are built from `run` blocks plus assertions.

```hcl
run "defaults" {
  module {
    source = "./"
  }

  assert {
    condition     = output.instance_shape == "VM.Standard.E6.Flex"
    error_message = "The default instance shape should match the expected profile."
  }
}
```

## Plan-mode tests

Prefer plan mode when you want to validate expressions, defaults, validation rules, and derived outputs without creating resources.

```hcl
run "server_defaults_plan" {
  command = "plan"

  module {
    source = "./"
  }

  variables {
    project_name     = "im"
    compartment_ocid = "ocid1.compartment.oc1..example"
    servers = {
      api = {
        compartment   = "compute"
        shape_profile = "x86_small"
      }
    }
  }

  assert {
    condition     = length(output.server_public_ips) == 1
    error_message = "One server definition should produce one public IP output entry."
  }
}
```

Use plan mode for:

- variable validation
- locals normalization
- resource count and for_each logic
- output shapes and derived values
- regression coverage for module wiring

## Apply-mode tests

Use apply mode only when you need real provider interaction.

```hcl
run "integration_apply" {
  module {
    source = "./"
  }

  assert {
    condition     = output.instance_id != ""
    error_message = "The applied instance should expose a non-empty instance_id output."
  }
}
```

In this repo, avoid apply-based tests against OCI unless the user explicitly wants live integration coverage and accepts the cost and credential requirements.

## Variables

Use `variables` blocks to set test inputs.

```hcl
variables {
  region = "sa-vinhedo-1"
}

run "custom_input" {
  command = "plan"

  module {
    source = "./"
  }

  variables {
    project_name = "im-test"
  }

  assert {
    condition     = var.project_name == "im-test"
    error_message = "The run-specific variable override should be visible to the test."
  }
}
```

## Chaining runs

Use outputs from one run as inputs to another when the scenario genuinely needs staged behavior.

```hcl
run "first_run" {
  module {
    source = "./modules/server"
  }

  output "instance_id" {
    value = "ocid1.instance.oc1..example"
  }
}

run "second_run" {
  command = "plan"

  module {
    source = "./modules/server"
  }

  variables {
    existing_instance_id = run.first_run.output.instance_id
  }
}
```

## Assertions

Keep assertions specific and business-meaningful.

Good assertions:

- verify explicit output structure
- verify a normalized local resolved the intended value
- verify validation catches a bad input
- verify important tags, names, or OCI placement logic

Weak assertions:

- checking only that every value is non-null
- repeating implementation details that are unlikely to regress
- asserting provider-computed attributes in plan-mode tests

```hcl
assert {
  condition     = can(regex("^im-", output.server_names["api"]))
  error_message = "Server names should be prefixed with the project name."
}
```

## Expected failures

Use `expect_failures` when the purpose of the test is to confirm validation rejects an invalid input.

```hcl
run "reject_missing_compartment" {
  command = "plan"

  module {
    source = "./"
  }

  variables {
    project_name     = "im"
    compartment_ocid = "ocid1.compartment.oc1..example"
    servers = {
      api = {
        shape_profile = "x86_small"
      }
    }
  }

  expect_failures = [
    var.servers,
  ]
}
```

This pattern is especially useful in this repo for alias validation, compartment resolution, and shape-profile validation.

## Test strategy for this repository

Prefer tests that exercise the repository's real invariants:

- every server resolves an explicit compartment alias
- reserved public IPs stay aligned with the server compartment
- `server_defaults` are applied consistently
- shape-profile lookup stays stable
- outputs preserve predictable map keys based on server name

Prefer not to test:

- provider-generated IDs in plan mode
- exact full provider payloads for complex OCI resources
- large end-to-end live applies unless the user explicitly requests integration testing

## CI guidance

For automated validation, prefer this order:

```bash
cd terraform
tofu fmt -check -recursive
tofu init
tofu validate
tofu test -verbose
```

## Troubleshooting

- If tests fail before evaluation, run `tofu init` again.
- If a plan-mode test references provider-computed values, rewrite the assertion to target configuration intent rather than runtime state.
- If an apply-mode test is flaky, reduce scope and isolate the resource or module under test.
- If credentials are unavailable, convert the scenario to plan mode where practical.

## Completion Checklist

Before claiming a test change is complete:

1. Run `tofu fmt -recursive` if you edited HCL.
2. Run `tofu test` for the affected scope.
3. If you intentionally skipped live apply-based coverage, say so explicitly.
