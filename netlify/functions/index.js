// Netlify 环境变量注入插件
import fs from 'fs';
import path from 'path';

export default {
  onPostBuild: async ({ constants, utils }) => {
    const { PUBLISH_DIR } = constants;
    const filesToProcess = [
      path.join(PUBLISH_DIR, 'index.html'),
      path.join(PUBLISH_DIR, 'test-env.html')
    ];
    
    // 检查环境变量是否存在
    if (!process.env.QWEN_API_KEY) {
      return utils.build.failPlugin('缺少必要的环境变量: QWEN_API_KEY');
    }
    
    if (!process.env.API_URL) {
      return utils.build.failPlugin('缺少必要的环境变量: API_URL');
    }
    
    // 处理每个文件
    for (const filePath of filesToProcess) {
      // 检查文件是否存在
      if (!fs.existsSync(filePath)) {
        console.log(`文件不存在，跳过处理: ${filePath}`);
        continue;
      }
      
      try {
        // 读取文件内容
        let content = fs.readFileSync(filePath, 'utf8');
        
        // 替换环境变量占位符
        content = content.replace(/{{ QWEN_API_KEY }}/g, process.env.QWEN_API_KEY);
        content = content.replace(/{{ API_URL }}/g, process.env.API_URL);
        
        // 写回文件
        fs.writeFileSync(filePath, content, 'utf8');
        
        console.log(`成功注入环境变量到 ${path.basename(filePath)}`);
      } catch (error) {
        return utils.build.failPlugin(`注入环境变量到 ${path.basename(filePath)} 失败: ${error.message}`);
      }
    }
  }
};