from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


class DeepSeekClient:
    def __init__(self, model_name="deepseek-ai/deepseek-coder-1.3b-instruct"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self._load_model()

    def _load_model(self):
        """加载DeepSeek模型"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
        except Exception as e:
            print(f"模型加载失败: {e}")
            # 可以设置降级方案

    def generate_code(self, prompt, max_length=500):
        """代码生成"""
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)