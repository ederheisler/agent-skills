import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

export async function serverValidate(data: unknown) {
  const schema = z.object({
    email: z.string().email(),
    password: z.string().min(8),
  })
  return schema.parse(data)
}
