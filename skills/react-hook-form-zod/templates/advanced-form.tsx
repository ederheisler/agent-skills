import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email'),
  items: z.array(
    z.object({
      name: z.string().min(1, 'Item name required'),
      quantity: z.coerce.number().min(1, 'Quantity must be at least 1'),
    })
  ).min(1, 'At least one item required'),
})

type FormData = z.infer<typeof schema>

export function AdvancedForm() {
  const { control, register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: '',
      email: '',
      items: [{ name: '', quantity: 1 }],
    },
  })

  const onSubmit = (data: FormData) => {
    console.log(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label>Name</label>
        <input {...register('name')} />
        {errors.name && <span>{errors.name.message}</span>}
      </div>

      <div>
        <label>Email</label>
        <input {...register('email')} />
        {errors.email && <span>{errors.email.message}</span>}
      </div>

      <div>
        <label>Items</label>
        {errors.items && <span>{errors.items.message}</span>}
      </div>

      <button type="submit">Submit</button>
    </form>
  )
}
