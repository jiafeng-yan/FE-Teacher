import { useState } from 'react'
import { uploadAPI } from '../services/api'

export default function DocumentUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setResult(null)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('请选择文件')
      return
    }

    setUploading(true)
    setError(null)
    setResult(null)

    try {
      const response = await uploadAPI.uploadDocument(file)
      setResult(response)
      setFile(null)
      // 重置文件输入
      document.getElementById('file-input').value = ''
      onUploadSuccess?.()
    } catch (err) {
      setError(err.response?.data?.detail || '上传失败，请重试')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">上传知识库文档</h2>
      
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
        <input
          id="file-input"
          type="file"
          onChange={handleFileChange}
          accept=".pdf,.txt,.doc,.docx,.ppt,.pptx,.md"
          className="hidden"
        />
        <label
          htmlFor="file-input"
          className="cursor-pointer inline-block px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          选择文件
        </label>
        {file && (
          <div className="mt-4">
            <p className="text-gray-600">已选择: {file.name}</p>
            <p className="text-sm text-gray-500">大小: {(file.size / 1024 / 1024).toFixed(2)} MB</p>
          </div>
        )}
      </div>

      <div className="text-sm text-gray-600">
        <p>支持的文件格式：</p>
        <ul className="list-disc list-inside mt-2 space-y-1">
          <li>PDF (.pdf)</li>
          <li>文本文件 (.txt, .md)</li>
          <li>Word 文档 (.doc, .docx)</li>
          <li>PowerPoint (.ppt, .pptx)</li>
        </ul>
      </div>

      {file && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="w-full px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {uploading ? '上传中...' : '上传文档'}
        </button>
      )}

      {result && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-green-800 font-semibold">上传成功！</p>
          <p className="text-green-600 text-sm mt-1">
            文件: {result.filename}
          </p>
          <p className="text-green-600 text-sm">
            已处理 {result.chunks_count} 个文档片段
          </p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-semibold">上传失败</p>
          <p className="text-red-600 text-sm mt-1">{error}</p>
        </div>
      )}
    </div>
  )
}

