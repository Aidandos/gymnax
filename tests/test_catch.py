import jax
import bsuite
import gymnax
from bsuite.environments import catch
import unittest, math
import numpy as np


class TestCatch(unittest.TestCase):
    num_episodes, num_steps = 1000, 9
    tolerance = 1e-04
    env_name = "Catch-bsuite"

    def test_catch_step(self):
        """ Test a step transition for the env. """
        env = catch.Catch()
        rng, reset, step, env_params = gymnax.make(TestCatch.env_name)

        # Loop over test episodes
        for ep in range(TestCatch.num_episodes):
            timestep = env.reset()
            # Loop over test episode steps
            for s in range(TestCatch.num_steps):
                action = np.random.choice([0, 1, 2])
                state_suite = np.array([env._ball_x, env._ball_y,
                                        env._paddle_x, env._paddle_y, 0,
                                        env._reset_next_step]).copy()
                timestep = env.step(action)
                obs_suite = timestep.observation
                reward_suite = timestep.reward
                done_suite = 1 - (timestep.discount is None)

                rng, rng_input = jax.random.split(rng)
                obs_jax, state_jax, reward_jax, done_jax, _ = step(rng_input,
                                                                   env_params, state_suite,
                                                                   action)

                # Check for correctness of transitions
                assert math.isclose(reward_suite, reward_jax,
                                    rel_tol=TestCatch.tolerance)
                self.assertEqual(done_suite, done_jax)
                assert np.allclose(obs_suite, obs_jax,
                                   atol=TestCatch.tolerance)

    def test_catch_reset(self):
        """ Test reset obs/state is in space of OpenAI version. """
        env = catch.Catch()
        observation_space = env.observation_spec()
        rng, reset, step, env_params = gymnax.make(TestCatch.env_name)
        for ep in range(TestCatch.num_episodes):
            rng, rng_input = jax.random.split(rng)
            obs, state = reset(rng_input, env_params)
            self.assertTrue(obs.shape == env.observation_spec().shape)
            # Check observation space
            self.assertTrue(env.observation_spec().minimum
                            <= obs[0][0]
                            <= env.observation_spec().maximum)
