// =============================================================================
// EditItemDialog Component
// Modal for creating and editing RAID items
// =============================================================================

import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useCreateItem, useUpdateItem } from "@/hooks/useItems"
import type { Item, ItemType, Workstream } from "@/types"
import { ITEM_TYPES } from "@/types"

// =============================================================================
// Validation Schema
// =============================================================================

const itemSchema = z.object({
  type: z.enum([
    "Budget",
    "Risk",
    "Action Item",
    "Issue",
    "Decision",
    "Deliverable",
    "Plan Item",
  ]),
  title: z.string().min(1, "Title is required").max(500, "Title too long"),
  description: z.string().optional(),
  workstream_id: z.string().nullable(),
  assigned_to: z.string().max(255).optional(),
  start_date: z.string().optional(),
  finish_date: z.string().optional(),
  deadline: z.string().optional(),
  percent_complete: z.number().min(0).max(100),
  priority: z.string().max(50).optional(),
  draft: z.boolean(),
  client_visible: z.boolean(),
})

type ItemFormData = z.infer<typeof itemSchema>

// =============================================================================
// Component Props
// =============================================================================

interface EditItemDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  projectId: string
  item?: Item | null  // null for create, Item for edit
  workstreams: Workstream[]
}

// =============================================================================
// Component
// =============================================================================

export function EditItemDialog({
  open,
  onOpenChange,
  projectId,
  item,
  workstreams,
}: EditItemDialogProps) {
  const isEditing = !!item
  const createItem = useCreateItem(projectId)
  const updateItem = useUpdateItem(projectId, item?.id || "")

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ItemFormData>({
    resolver: zodResolver(itemSchema),
    defaultValues: {
      type: "Action Item",
      title: "",
      description: "",
      workstream_id: null,
      assigned_to: "",
      start_date: "",
      finish_date: "",
      deadline: "",
      percent_complete: 0,
      priority: "",
      draft: false,
      client_visible: true,
    },
  })

  // Reset form when item changes
  useEffect(() => {
    if (item) {
      reset({
        type: item.type,
        title: item.title,
        description: item.description || "",
        workstream_id: item.workstream_id,
        assigned_to: item.assigned_to || "",
        start_date: item.start_date || "",
        finish_date: item.finish_date || "",
        deadline: item.deadline || "",
        percent_complete: item.percent_complete,
        priority: item.priority || "",
        draft: item.draft,
        client_visible: item.client_visible,
      })
    } else {
      reset({
        type: "Action Item",
        title: "",
        description: "",
        workstream_id: null,
        assigned_to: "",
        start_date: "",
        finish_date: "",
        deadline: "",
        percent_complete: 0,
        priority: "",
        draft: false,
        client_visible: true,
      })
    }
  }, [item, reset])

  // Watch values for controlled components
  const percentComplete = watch("percent_complete")
  const selectedType = watch("type")
  const selectedWorkstream = watch("workstream_id")

  // Form submission
  const onSubmit = async (data: ItemFormData) => {
    try {
      const payload = {
        ...data,
        description: data.description || null,
        workstream_id: data.workstream_id || null,
        assigned_to: data.assigned_to || null,
        start_date: data.start_date || null,
        finish_date: data.finish_date || null,
        deadline: data.deadline || null,
        priority: data.priority || null,
      }

      if (isEditing) {
        await updateItem.mutateAsync(payload)
      } else {
        await createItem.mutateAsync(payload)
      }
      onOpenChange(false)
    } catch (error) {
      console.error("Failed to save item:", error)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? `Edit Item #${item?.item_num}` : "Create New Item"}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Type and Title row */}
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Type *</Label>
              <Select
                value={selectedType}
                onValueChange={(value) => setValue("type", value as ItemType)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {ITEM_TYPES.map((type) => (
                    <SelectItem key={type} value={type}>
                      {type}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="col-span-2 space-y-2">
              <Label>Title *</Label>
              <Input {...register("title")} placeholder="Item title" />
              {errors.title && (
                <p className="text-xs text-destructive">{errors.title.message}</p>
              )}
            </div>
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label>Description</Label>
            <Textarea
              {...register("description")}
              placeholder="Detailed description..."
              rows={3}
            />
          </div>

          {/* Workstream and Assigned To */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Workstream</Label>
              <Select
                value={selectedWorkstream || "none"}
                onValueChange={(value) =>
                  setValue("workstream_id", value === "none" ? null : value)
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select workstream" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  {workstreams.map((ws) => (
                    <SelectItem key={ws.id} value={ws.id}>
                      {ws.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Assigned To</Label>
              <Input {...register("assigned_to")} placeholder="Person name" />
            </div>
          </div>

          {/* Dates row */}
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Start Date</Label>
              <Input type="date" {...register("start_date")} />
            </div>
            <div className="space-y-2">
              <Label>Finish Date</Label>
              <Input type="date" {...register("finish_date")} />
            </div>
            <div className="space-y-2">
              <Label>Deadline</Label>
              <Input type="date" {...register("deadline")} />
            </div>
          </div>

          {/* Progress slider */}
          <div className="space-y-2">
            <div className="flex justify-between">
              <Label>Progress</Label>
              <span className="text-sm text-muted-foreground">
                {percentComplete}%
              </span>
            </div>
            <Slider
              value={[percentComplete]}
              onValueChange={(values) => setValue("percent_complete", values[0] ?? 0)}
              min={0}
              max={100}
              step={5}
            />
          </div>

          {/* Priority */}
          <div className="space-y-2">
            <Label>Priority</Label>
            <Select
              value={watch("priority") || "none"}
              onValueChange={(value) =>
                setValue("priority", value === "none" ? "" : value)
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Select priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">None</SelectItem>
                <SelectItem value="Low">Low</SelectItem>
                <SelectItem value="Medium">Medium</SelectItem>
                <SelectItem value="High">High</SelectItem>
                <SelectItem value="Critical">Critical</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Visibility options */}
          <div className="flex gap-6">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                {...register("draft")}
                className="rounded border-input"
              />
              Draft (hidden from most views)
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                {...register("client_visible")}
                className="rounded border-input"
              />
              Client Visible
            </label>
          </div>

          {/* Footer buttons */}
          <DialogFooter className="pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting
                ? "Saving..."
                : isEditing
                  ? "Save Changes"
                  : "Create Item"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default EditItemDialog
