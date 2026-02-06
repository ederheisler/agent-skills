# Quick Fixes

| If suggested... | Use instead... |
|----------------|----------------|
| No `defaultValues` | Always provide `defaultValues: { field: '' }` |
| `key={index}` in useFieldArray | `key={field.id}` |
| Partial field props | Spread `{...field}` |
| `errors.a.b.message` | `errors.a?.b?.message` |
| Client-only validation | Validate on server too |
| Missing refinement path | Add `path: ['fieldName']` |
