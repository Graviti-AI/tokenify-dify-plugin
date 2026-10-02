# Tokenify for Dify

Use [Tokenify](https://www.tokenify.dev) models in Dify. Tokenify serves DeepSeek V4 and GLM models through an OpenAI-compatible API at `https://api.tokenify.dev/v1`, billed per token, with credit that never expires.

## Setup

1. Create an account and an API key at https://www.tokenify.dev/app/signup.
2. In Dify, open **Settings → Model Provider**, find **Tokenify** and click **Add Model**.
3. Enter the model ID exactly as Tokenify lists it, for example `deepseek/deepseek-v4-pro`, and your API key.
4. Optional: set the context size and the max-token cap, and turn on vision for models that accept images (`deepseek/deepseek-v4.1-flash`, `z-ai/glm-5.3-flash`).

The current model list with prices is at https://www.tokenify.dev/models/ and from `GET https://api.tokenify.dev/v1/models`.

| Model ID | Notes |
|---|---|
| `deepseek/deepseek-v4.1-flash` | fast, accepts images |
| `deepseek/deepseek-v4-pro` | reasoning, agents and code |
| `deepseek/deepseek-v4-flash` | fast |
| `z-ai/glm-5.3-flash` | fast, accepts images |
| `z-ai/glm-5.2` | reasoning |

## Notes

- The endpoint is fixed to `https://api.tokenify.dev/v1`; the plugin calls no other host.
- Streaming and tool calling are supported.
- Reasoning models return their reasoning in `reasoning_content`; reasoning tokens are billed at the output rate.

## Support

support@tokenify.dev · Docs: https://www.tokenify.dev/docs/
