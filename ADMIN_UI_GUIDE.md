# Admin Dashboard UI Guide

## Overview

Visual guide to the enhanced Admin Dashboard with Enable/Disable/Edit functionality.

## Instructors Table

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ Instructors                                                          [Add Instructor]        │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ Name          │ Username     │ Email              │ Department │ Status    │ Actions        │
├───────────────┼──────────────┼────────────────────┼────────────┼───────────┼────────────────┤
│ John Smith    │ instructor1  │ john@example.com   │ CS         │ [Enabled] │ [Disable] [Edit] [Delete] │
│ Jane Doe      │ instructor2  │ jane@example.com   │ Math       │ [Disabled]│ [Enable]  [Edit] [Delete] │
│ Bob Johnson   │ instructor3  │ bob@example.com    │ Physics    │ [Enabled] │ [Disable] [Edit] [Delete] │
└───────────────┴──────────────┴────────────────────┴────────────┴───────────┴────────────────┘
```

### Status Badges
- **[Enabled]** - Green badge, user can login
- **[Disabled]** - Red badge, user cannot login

### Action Buttons
- **[Disable]** - Orange button, disables the account
- **[Enable]** - Green button, enables the account
- **[Edit]** - Blue button, opens edit modal
- **[Delete]** - Red button, deletes the account

## Students Table

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Students                                                                      [Add Student]               │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Student ID │ Name          │ Email              │ Department │ Face Reg. │ Status    │ Actions           │
├────────────┼───────────────┼────────────────────┼────────────┼───────────┼───────────┼───────────────────┤
│ S001       │ Alice Brown   │ alice@example.com  │ CS         │ [Yes]     │ [Enabled] │ [Disable] [Edit] [Delete] │
│ S002       │ Charlie Davis │ charlie@example.com│ Math       │ [No]      │ [Disabled]│ [Enable]  [Edit] [Delete] │
│ S003       │ Diana Evans   │ diana@example.com  │ Physics    │ [Yes]     │ [Enabled] │ [Disable] [Edit] [Delete] │
└────────────┴───────────────┴────────────────────┴────────────┴───────────┴───────────┴───────────────────┘
```

### Status Badges
- **[Enabled]** - Green badge, user can login
- **[Disabled]** - Red badge, user cannot login

### Face Registration Badges
- **[Yes]** - Green badge, face is registered
- **[No]** - Red badge, face not registered

### Action Buttons
- **[Disable]** - Orange button, disables the account
- **[Enable]** - Green button, enables the account
- **[Edit]** - Blue button, opens edit modal
- **[Delete]** - Red button, deletes the account

## Edit Instructor Modal

```
┌─────────────────────────────────────────────┐
│  Edit Instructor                      [X]   │
├─────────────────────────────────────────────┤
│                                             │
│  Full Name:                                 │
│  ┌───────────────────────────────────────┐ │
│  │ John Smith                            │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Email:                                     │
│  ┌───────────────────────────────────────┐ │
│  │ john@example.com                      │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Department:                                │
│  ┌───────────────────────────────────────┐ │
│  │ Computer Science                      │ │
│  └───────────────────────────────────────┘ │
│                                             │
│         [Save]           [Cancel]           │
│                                             │
└─────────────────────────────────────────────┘
```

## Edit Student Modal

```
┌─────────────────────────────────────────────┐
│  Edit Student                         [X]   │
├─────────────────────────────────────────────┤
│                                             │
│  Full Name:                                 │
│  ┌───────────────────────────────────────┐ │
│  │ Alice Brown                           │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Email:                                     │
│  ┌───────────────────────────────────────┐ │
│  │ alice@example.com                     │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Department:                                │
│  ┌───────────────────────────────────────┐ │
│  │ Computer Science                      │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Year:                                      │
│  ┌───────────────────────────────────────┐ │
│  │ 3                                     │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Section:                                   │
│  ┌───────────────────────────────────────┐ │
│  │ A                                     │ │
│  └───────────────────────────────────────┘ │
│                                             │
│         [Save]           [Cancel]           │
│                                             │
└─────────────────────────────────────────────┘
```

## User Interactions

### 1. Disable User Flow
```
Admin clicks [Disable] button
    ↓
Status badge changes to [Disabled] (red)
    ↓
User tries to login
    ↓
Error: "Account is disabled. Please contact administrator."
```

### 2. Enable User Flow
```
Admin clicks [Enable] button
    ↓
Status badge changes to [Enabled] (green)
    ↓
User can login successfully
```

### 3. Edit User Flow
```
Admin clicks [Edit] button
    ↓
Modal opens with current values
    ↓
Admin modifies fields
    ↓
Admin clicks [Save]
    ↓
Modal closes
    ↓
Table updates with new values
    ↓
Success toast: "User updated successfully"
```

### 4. Delete User Flow
```
Admin clicks [Delete] button
    ↓
Confirmation dialog: "Are you sure you want to delete this user?"
    ↓
Admin confirms
    ↓
User removed from table
    ↓
Success toast: "User deleted successfully"
```

## Toast Notifications

### Success Messages
- ✅ "Instructor status updated"
- ✅ "Student status updated"
- ✅ "Instructor updated successfully"
- ✅ "Student updated successfully"
- ✅ "Instructor deleted successfully"
- ✅ "Student deleted successfully"

### Error Messages
- ❌ "Failed to update instructor"
- ❌ "Failed to update student"
- ❌ "Failed to delete instructor"
- ❌ "Failed to delete student"

## Color Scheme

### Status Badges
- **Enabled**: Green background (#dcfce7), Green text (#166534)
- **Disabled**: Red background (#fee2e2), Red text (#991b1b)

### Action Buttons
- **Enable**: Green text (#059669)
- **Disable**: Orange text (#ea580c)
- **Edit**: Blue text (#2563eb)
- **Delete**: Red text (#dc2626)

### Hover Effects
- **Enable**: Darker green (#047857)
- **Disable**: Darker orange (#c2410c)
- **Edit**: Darker blue (#1d4ed8)
- **Delete**: Darker red (#b91c1c)

## Responsive Design

### Desktop (>768px)
- Full table layout
- All columns visible
- Modal centered on screen

### Tablet (768px - 1024px)
- Scrollable table
- All columns visible
- Modal adjusted for screen size

### Mobile (<768px)
- Horizontal scroll for table
- Stacked form fields in modal
- Touch-friendly button sizes

## Accessibility

### Keyboard Navigation
- Tab through buttons
- Enter to activate
- Escape to close modal

### Screen Readers
- Descriptive button labels
- Status announcements
- Form field labels

### Color Contrast
- WCAG AA compliant
- High contrast for status badges
- Clear button states

## Tips

1. **Quick Toggle**: Click status badge area to toggle (future enhancement)
2. **Bulk Actions**: Select multiple users for batch operations (future enhancement)
3. **Search/Filter**: Use search to find specific users quickly (future enhancement)
4. **Sort**: Click column headers to sort (future enhancement)

## Common Workflows

### Onboarding New Instructor
1. Click [Add Instructor]
2. Fill in details
3. Click [Add]
4. Instructor appears in table with [Enabled] status

### Temporarily Disable Student
1. Find student in table
2. Click [Disable]
3. Status changes to [Disabled]
4. Student cannot login until re-enabled

### Update Instructor Information
1. Find instructor in table
2. Click [Edit]
3. Modify fields in modal
4. Click [Save]
5. Changes reflected immediately

### Remove Graduated Student
1. Find student in table
2. Click [Delete]
3. Confirm deletion
4. Student removed from system

---

**Note**: This is a text-based representation. The actual UI uses modern web components with smooth animations and transitions.
