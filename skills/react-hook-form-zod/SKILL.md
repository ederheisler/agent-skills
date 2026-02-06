---
name: react-hook-form-zod
description: "Build type-safe validated forms using React Hook Form v7 and Zod v4. Single schema works on client and server with full TypeScript inference via z.infer. Use when building forms, multi-step wizards, or fixing uncontrolled warnings, resolver errors, useFieldArray issues, performance problems with large forms."
---

# React Hook Form + Zod Validation

**Status**: Production Ready
**Last Verified**: 2026-01-20
**Latest Versions**: react-hook-form@7.71.1, zod@4.3.5, @hookform/resolvers@5.2.2

---


## Quick Start

```bash
bun add react-hook-form@7.70.0 zod@4.3.5 @hookform/resolvers@5.2.2
```

**Basic Form Pattern**:
```typescript
const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
})

type FormData = z.infer<typeof schema>

const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
  resolver: zodResolver(schema),
  defaultValues: { email: '', password: '' },
})

<form onSubmit={handleSubmit(onSubmit)}>
  <input {...register('email')} />
  {errors.email && <span role="alert">{errors.email.message}</span>}
</form>
```

**Server Validation** (CRITICAL - never skip):
```typescript
// SAME schema on server
const data = schema.parse(await req.json())
```

---


## Key Patterns

**useForm Options** (validation modes):
- `mode: 'onSubmit'` (default) - Best performance
- `mode: 'onBlur'` - Good balance
- `mode: 'onChange'` - Live feedback, more re-renders
- `shouldUnregister: true` - Remove field data when unmounted (use for multi-step forms)

**Zod Refinements** (cross-field validation):
```typescript
z.object({ password: z.string(), confirm: z.string() })
  .refine((data) => data.password === data.confirm, {
    message: "Passwords don't match",
    path: ['confirm'],
  })
```

**Zod Transforms**:
```typescript
z.string().transform((val) => val.toLowerCase())
z.string().transform(parseInt).refine((v) => v > 0)
```

**zodResolver** connects Zod to React Hook Form, preserving type safety

---


## Registration

**register** (for standard HTML inputs):
```typescript
<input {...register('email')} />
```

**Controller** (for third-party components):
```typescript
<Controller
  name="category"
  control={control}
  render={({ field }) => <CustomSelect {...field} />}
/>
```

---


## Error Handling

**Display errors**:
```typescript
{errors.email && <span role="alert">{errors.email.message}</span>}
{errors.address?.street?.message}
```

**Server errors**:
```typescript
const onSubmit = async (data) => {
  const res = await fetch('/api/submit', { method: 'POST', body: JSON.stringify(data) })
  if (!res.ok) {
    const { errors: serverErrors } = await res.json()
    Object.entries(serverErrors).forEach(([field, msg]) => setError(field, { message: msg }))
  }
}
```

---


## Advanced Patterns

**useFieldArray** (dynamic lists):
```typescript
const { fields, append, remove } = useFieldArray({ control, name: 'contacts' })

{fields.map((field, index) => (
  <div key={field.id}>
    <input {...register(`contacts.${index}.name` as const)} />
    <button onClick={() => remove(index)}>Remove</button>
  </div>
))}
<button onClick={() => append({ name: '', email: '' })}>Add</button>
```

**Multi-Step Forms**:
```typescript
const step1 = z.object({ name: z.string(), email: z.string().email() })
const step2 = z.object({ address: z.string() })
const fullSchema = step1.merge(step2)

const nextStep = async () => {
  const isValid = await trigger(['name', 'email'])
  if (isValid) setStep(2)
}
```

**Conditional Validation**:
```typescript
z.discriminatedUnion('accountType', [
  z.object({ accountType: z.literal('personal'), name: z.string() }),
  z.object({ accountType: z.literal('business'), companyName: z.string() }),
])
```

---


## Performance

- Use `register` (uncontrolled) over `Controller` (controlled)
- Use `watch('email')` not `watch()` (isolates re-renders)
- Use `mode: "onSubmit"` for large forms

### Large Forms (300+ Fields)

Forms with 300+ fields with resolver can freeze for 10-15 seconds.

**Workarounds**:
1. Don't destructure `formState` - read inline only
2. Use `mode: "onSubmit"` (not onChange)
3. Split into sub-forms (50-60 fields each)
4. Lazy render fields with tabs/accordion

---


## Critical Rules

- Always set `defaultValues` (prevents uncontrolled→controlled warnings)
- Validate on BOTH client and server
- Use `field.id` as key in useFieldArray (not index)
- Spread `{...field}` in Controller render
- Use `z.infer<typeof schema>` for type inference
- Never skip server validation (security!)

---


## Known Issues (20 Prevented)

1. **Zod v4 Type Inference** - Use `z.infer<typeof schema>` explicitly. Resolved in v7.66.x+.

2. **Uncontrolled→Controlled Warning** - Always set `defaultValues`

3. **Nested Object Errors** - Use optional chaining: `errors.address?.street?.message`

4. **Array Field Re-renders** - Use `key={field.id}` in useFieldArray

5. **Async Validation Race Conditions** - Debounce, cancel pending

6. **Server Error Mapping** - Use `setError()` to map errors

7. **Default Values Not Applied** - Set in useForm options

8. **Controller Field Not Updating** - Always spread `{...field}`

9. **useFieldArray Key Warnings** - Use `field.id` not index

10. **Schema Refinement Error Paths** - Specify `path` in refinement

11. **Transform vs Preprocess** - Use `transform` for output

12. **Multiple Resolver Conflicts** - Use single resolver

13. **Zod v4 Optional Fields Bug** - Use `.nullish()` or `.or(z.literal(""))`

14. **useFieldArray Primitive Arrays** - Wrap primitives: `[{ value: "string" }]`

15. **useFieldArray SSR ID Mismatch** - Use client-only rendering

16. **Next.js reset() Bug** - Fixed in v7.65.0+

17. **Validation Race Condition** - Don't derive validity from errors alone

18. **ZodError Thrown in Beta** - Avoid beta versions

19. **Large Form Performance** - See Performance section

20. **shadcn Form Import Confusion** - Import Form from shadcn, not react-hook-form

---


## shadcn/ui Integration

shadcn deprecated the Form component. Use the Field component for new implementations.

**Common Import Mistake**:
```typescript
// Correct:
import { useForm } from "react-hook-form";
import { Form, FormField, FormItem } from "@/components/ui/form";

// Wrong:
import { useForm, Form } from "react-hook-form";
```

---


## Bundled Resources

**Templates**: basic-form.tsx, advanced-form.tsx, shadcn-form.tsx, server-validation.ts, async-validation.tsx, dynamic-fields.tsx, multi-step-form.tsx, package.json

**References**: zod-schemas-guide.md, rhf-api-reference.md, error-handling.md, performance-optimization.md, shadcn-integration.md, top-errors.md

---


**License**: MIT | **Last Verified**: 2026-01-20 | **Skill Version**: 2.1.0
