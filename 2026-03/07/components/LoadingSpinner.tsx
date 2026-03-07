export default function LoadingSpinner() {

  return (
    <div className="flex items-center gap-2 text-white">
      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin "/>
      Generating...
    </div>
  )
}